import re
import aiohttp
from .soundcloud_client import SoundCloudClient
from .schemas import Track, User
from cachetools import cached, TTLCache
import logging

log = logging.getLogger(__name__)

# Create a cache with a time-to-live (TTL) of 300 seconds and a max size of 100 items
cache = TTLCache(maxsize=100, ttl=60 * 60)


class SoundCloud(SoundCloudClient):
    async def search(self, query: str, limit: int = 10) -> list[Track]:
        response = await super().search(query, limit)
        return [Track.from_dict(item) for item in response.get("collection", [])]

    async def get_track(self, _id):
        return Track.from_dict(await super().get_track(_id))

    async def get_user(self, _id):
        return User.from_dict(await super().get_user(_id))

    async def get_stream_url(self, track: Track) -> str:
        """
        Fetches the stream URL for a given track.
        This method retrieves the streaming URL for a track by iterating through
        the available transcodings in the track's media. It selects the first
        transcoding with a "progressive" format protocol and fetches the stream
        URL using the provided client ID.
        Args:
            track (Track): The track object containing media information.
        Returns:
            str: The URL for streaming the track.
        Raises:
            aiohttp.ClientError: If there is an issue with the HTTP request.
            KeyError: If the expected "url" key is not found in the response JSON.
        """

        log.debug(f"Fetching stream URL for track: {track.id}")
        async with aiohttp.ClientSession() as session:
            for transcoding in track.media:
                if transcoding.format_protocol == "progressive":
                    trans_url = transcoding.url
                    async with session.get(
                        f"{trans_url}?client_id={self.client_id}"
                    ) as resp:
                        stream_info = await resp.json()
                        stream_url: str = stream_info["url"]
                        break
            return stream_url
