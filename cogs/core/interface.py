from typing import Protocol

from .schemas import SongDTO


class ISongAPI(Protocol):
    async def get_song(self, query: str) -> SongDTO:
        """
        get song
        :param query:
        :return SongDTO:
        :raise NotFoundSong:
        """
        pass
