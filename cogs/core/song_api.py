import logging

from cachetools import TTLCache
from yt_dlp import YoutubeDL

from .exception import NotFoundSong
from .interface import ISongAPI
from .schemas import create_SongDTO, SongDTO
import asyncio
from concurrent.futures import  ThreadPoolExecutor

executor = ThreadPoolExecutor(max_workers=2)

log = logging.getLogger(__name__)

class YouTubeClient(ISongAPI):
    def __init__(self):
        self.count_search = 2
        self.ydl_opts = {
            'quiet': True,
            'skip_download': True,
            'extract_flat': False,
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        self._cache = TTLCache(maxsize=100, ttl=1800)

    async def get_song(self, query:str)->SongDTO:
        """
        get song from YouTube
        :param query:
        :return SongDTO:
        :raise NotFoundVideo:
        """
        if query in self._cache:
            log.info(f"Get song from cache: {query}")
            return self._cache[query]

        func = self.__get_from_url if query.startswith('http') else self.__get_from_query
        log.info(f"Get song from YouTube: {query}")
        loop = asyncio.get_event_loop()
        info = await loop.run_in_executor(executor, func, query)
        if not info:
            log.info(f"Song not found: {query}")
            raise NotFoundSong
        log.info(f"Got song from YouTube: {query}")
        dto = create_SongDTO(info)
        self._cache[query] = dto
        return dto
        

    def __get_from_url(self, url:str):
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
        if not info:
            raise NotFoundSong
        return info

    def __get_from_query(self, query:str):
        rep = f'ytsearch{self.count_search}:{query} music'
        with YoutubeDL(self.ydl_opts) as ydl:
            info = ydl.extract_info(rep, download=False)
        
        if not info or 'entries' not in info:
            raise NotFoundSong
        
        info = min(
            (song for song in info['entries'] if song.get('duration')),
            key=lambda song: song['duration'],
            default=None
        )
        return info