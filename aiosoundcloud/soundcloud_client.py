import logging
import re
from typing import overload
import aiohttp

log = logging.getLogger(__name__)


class SoundCloudClient:
    def __init__(self, client_id: str | None = None):
        self.BASE_URL: str = "https://api-v2.soundcloud.com"
        self.client_id: str | None = client_id
        self.SHORT_URL_PREFIX: str = "https://on.soundcloud.com/"
        self.STANDARD_URL: str = "https://soundcloud.com/"

    async def search(
        self, query: str = "", limit: int = 10, genre: str | None = None
    ) -> dict:
        """
        Searches for tracks on SoundCloud based on the given query.
        Args:
            query (str): The search query string to look for tracks.
            limit (int, optional): The maximum number of results to return. Defaults to 10.
        Returns:
            dict: A dictionary containing the search results.
        Raises:
            Exception: If the request to the SoundCloud API fails or returns an error.
        """
        return await self.__search(query, limit, genre=genre, _type="tracks")

    async def search_playlists(
        self,
        query: str = "",
        limit: int = 10,
        genre: str | None = None,
        track_limit: int | None = None,
    ) -> dict:
        """
        Searches for playlists on SoundCloud based on the given query.
        Args:
            query (str): The search query string to look for playlists.
            limit (int, optional): The maximum number of results to return. Defaults to 10.
        Returns:
            dict: A dictionary containing the search results.
        Raises:
            Exception: If the request to the SoundCloud API fails or returns an error.
        """
        data = await self.__search(query, limit, genre=genre, _type="playlists")
        playlists: list[dict] = []
        for playlist in data["collection"]:
            playlists.append(await self.get_playlist(playlist["id"], limit=track_limit))
        return playlists

    @overload
    async def get_playlist(self, _id: int, limit: int | None) -> dict: ...

    @overload
    async def get_playlist(self, url: str, limit: int | None) -> dict: ...

    async def get_playlist(self, arg: str | int, limit: int | None) -> dict:
        """
        Retrieves a playlist by its ID or URL from SoundCloud.
        """
        # Якщо це int, конвертуємо в str
        if isinstance(arg, int) or (isinstance(arg, str) and arg.isdigit()):
            arg_str = str(arg)
            data = await self.__get_info_for_id("playlists", arg_str)
            return await self.__get_playlist_for_id(data, limit=limit)

        elif isinstance(arg, str) and (
            arg.startswith("https://soundcloud.com/")
            or arg.startswith(self.SHORT_URL_PREFIX)
        ):
            data = await self.fetch_resolved_url_info(arg)
            return await self.__get_playlist_for_id(data, limit=limit)

        raise ValueError("Invalid playlist identifier")

    async def fetch_resolved_url_info(self, url: str) -> dict:
        """
        Fetches and resolves information about a given SoundCloud URL.
        This method constructs a resolve API endpoint URL using the provided SoundCloud URL
        and sends an asynchronous request to retrieve the resolved information.
        Args:
            url (str): The SoundCloud URL to be resolved.
        Returns:
            dict: A dictionary containing the resolved information for the given URL.
        """
        if url.startswith(self.SHORT_URL_PREFIX):
            url = await self.__resolve_short(url)
        url = f"{self.BASE_URL}/resolve?url={url}"
        return await self.__sponce(url=url)

    async def get_track(self, _id: str):
        """
        Retrieve information about a specific track by its ID.
        Args:
            _id (str): The unique identifier of the track.
        Returns:
            dict: A dictionary containing the track's information.
        Raises:
            Exception: If the request to retrieve the track information fails.
        """

        return await self.__get_info_for_id("tracks", _id)

    async def get_user(self, _id: str) -> dict:
        """
        Retrieve information about a SoundCloud user by their ID.
        Args:
            _id (str): The unique identifier of the SoundCloud user.
        Returns:
            dict: A dictionary containing the user's information.
        """

        return await self.__get_info_for_id("users", _id)

    async def get_info_for_urn(self, urn: str):
        """
        Asynchronously retrieves information for a given URN (Uniform Resource Name).
        Args:
            urn (str): The URN string in the format 'namespace:id:type'.
        Returns:
            Any: The information retrieved for the specified URN.
        Raises:
            ValueError: If the URN format is incorrect.
        Notes:
            The URN is expected to be a string that can be split into three parts
            separated by colons. If the format is valid, the method delegates the
            retrieval to the private method `__get_info_for_id`.
        """

        urn = urn.split(":")
        if urn.__len__ == 3:
            return await self.__get_info_for_id(urn[1], urn[2])
        log.error("URN format is incorrect")
        raise ValueError("URN dot correct")

    async def __get_playlist_for_id(self, data: dict, limit: int = None) -> str:
        if data is None:
            raise ValueError("Playlist not found or invalid ID")
        if data.get("tracks") is None:
            raise ValueError("Playlist not found or invalid ID")
        data["tracks"] = [
            await self.get_track(track["id"]) for track in data["tracks"][:limit]
        ]
        return data

    async def __get_info_for_id(self, endpoint: str, _id: str):
        url = f"{self.BASE_URL}/{endpoint}/{_id}"
        return await self.__sponce(url=url)

    async def __sponce(
        self, url: str, params: dict[str, any] | None = None
    ) -> dict[str, any] | None:
        if self.client_id is None:
            await self.__extract_soundcloud_client_id()

        if params is None:
            params = {"client_id": self.client_id}
        else:
            params["client_id"] = self.client_id

        log.debug("Making GET request to %s", url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                elif response.status == 401:
                    log.error(
                        "Unauthorized access - client_id. Trying to refresh client_id..."
                    )
                    await self.__extract_soundcloud_client_id()
                    # Оновлюємо client_id у params
                    params["client_id"] = self.client_id
                    # Повторна спроба
                    async with session.get(url, params=params) as retry_response:
                        if retry_response.status == 200:
                            data = await retry_response.json()
                            return data
                        log.error(
                            f"Retry failed with status code {retry_response.status}"
                        )
                        return None
                else:
                    log.error(f"Request failed with status code {response.status}")
                    return None

    async def __resolve_short(self, short_url: str) -> dict:
        async with aiohttp.ClientSession() as session:
            async with session.get(short_url, allow_redirects=False) as resp:
                if "Location" not in resp.headers:
                    log.error("No Location header found")
                    return None
                real_url = resp.headers["Location"]
                return real_url

    async def __search(
        self,
        query: str,
        limit: int = 10,
        genre: str | None = None,
        _type: str = "tracks",
    ) -> dict:
        """
        Searches for tracks on SoundCloud based on the given query.
        Args:
            query (str): The search query string to look for tracks.
            limit (int, optional): The maximum number of results to return. Defaults to 10.
        Returns:
            dict: A dictionary containing the search results.
        Raises:
            Exception: If the request to the SoundCloud API fails or returns an error.
        """

        url = f"{self.BASE_URL}/search/{_type}?q={query}"

        params = {"limit": limit}
        if genre:
            params["filter.genre_or_tag"] = genre
        return await self.__sponce(url=url, params=params)

    async def __extract_soundcloud_client_id(self) -> str:
        """
        Asynchronously retrieves the SoundCloud client ID by parsing the SoundCloud homepage
        and its associated JavaScript files.
        Args:
            session (aiohttp.ClientSession): An active aiohttp session used to perform HTTP requests.
        Returns:
            str: The extracted SoundCloud client ID.
        Raises:
            RuntimeError: If the client ID cannot be found in the JavaScript files.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.STANDARD_URL) as resp:
                html = await resp.text()

            js_urls = re.findall(
                r'src="(https://a-v2\.sndcdn\.com/assets/\w+-\w+\.js)"', html
            )
            for js_url in js_urls:
                async with session.get(js_url) as js_resp:
                    js = await js_resp.text()
                    match = re.search(r'client_id\s*:\s*"(?P<client_id>\w+)"', js)
                    if match:
                        self.client_id = match.group("client_id")
        if not self.client_id:
            raise RuntimeError("client_id not found")
