import logging
import re
import aiohttp

from .interface import ISongAPI
from .schemas import SongDTO, song_dto_from_dict
from .exception import NotFoundSong
from cachetools import TTLCache, cached

log = logging.getLogger(__name__)
class SoundCloudClient(ISongAPI):
    def __init__(self):
        self._client_id = None
        self._cache = TTLCache(maxsize=100, ttl=3600)  # 1 hour TTL

    async def _get_client_id(self, session: aiohttp.ClientSession) -> str:
        if self._client_id:
            return self._client_id

        async with session.get("https://soundcloud.com") as resp:
            html = await resp.text()

        js_urls = re.findall(r'src="(https://a-v2\.sndcdn\.com/assets/\w+-\w+\.js)"', html)
        for js_url in js_urls:
            async with session.get(js_url) as js_resp:
                js = await js_resp.text()
                match = re.search(r'client_id\s*:\s*"(?P<client_id>\w+)"', js)
                if match:
                    self._client_id = match.group("client_id")
                    return self._client_id
        raise RuntimeError("client_id not found")

    async def get_song(self, query: str) -> SongDTO:
        if query in self._cache:
            log.info(f"cache hit {query}")
            return self._cache[query]
        
        log.info(f"requesting {query}")
        async with aiohttp.ClientSession() as session:
            client_id = await self._get_client_id(session)

            url = f"https://api-v2.soundcloud.com/search/tracks?q={query}&client_id={client_id}&limit=1"
            async with session.get(url) as resp:
                data:dict = await resp.json()
                tracks = data.get("collection", [])
                if not tracks:
                    raise NotFoundSong()
                track = tracks[0]

            # Витяг прямого стріму
            for transcoding in track["media"]["transcodings"]:
                if transcoding["format"]["protocol"] == "progressive":
                    trans_url = transcoding["url"]
                    async with session.get(f"{trans_url}?client_id={client_id}") as resp:
                        stream_info = await resp.json()
                        stream_url = stream_info["url"]
                        break
            else:
                raise NotFoundSong()

            # Формування DTO
            dto = song_dto_from_dict(stream_url=stream_url, **track)
            self._cache[query] = dto
            return dto