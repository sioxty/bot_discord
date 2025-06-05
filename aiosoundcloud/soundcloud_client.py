import logging
import aiohttp
from cachetools import TTLCache

log = logging.getLogger(__name__)


class SoundCloudClient:
    def __init__(self, client_id: str):
        self.BASE_URL = "https://api-v2.soundcloud.com"
        self.client_id: str = client_id

    async def search(self, query: str, limit: int = 10) -> dict:
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

        url = f"{self.BASE_URL}/search/tracks?q={query}"
        params = {"limit": limit, "client_id": self.client_id}
        return await self.__sponce(url=url, params=params)

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

    async def __get_info_for_id(self, endpoint: str, _id: str):
        url = f"{self.BASE_URL}/{endpoint}/{_id}"
        return await self.__sponce(url=url)

    async def __sponce(self, url, params=None) -> dict[str, any] | None:
        if params is None:
            params = {"client_id": self.client_id}
        log.info(f"Making GET request to %s", url)
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return None
