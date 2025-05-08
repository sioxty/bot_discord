from abc import ABC, abstractmethod

from .schemas import SongDTO


class ISongAPI(ABC):
    @abstractmethod
    async def get_song(self, query: str) -> SongDTO:
        """
        get song
        :param query:
        :return SongDTO:
        :raise NotFoundSong:
        """
        pass
