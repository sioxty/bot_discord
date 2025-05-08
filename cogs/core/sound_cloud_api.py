from sclib.asyncio import SoundcloudAPI

from .interface import ISongAPI
from .schemas import create_SongDTO


class SoundCloudClient(ISongAPI):
    def __init__(self, client_id):
        self.client_id = client_id
        self.client = SoundcloudAPI(client_id=client_id)

    async def get_song(self, url: str):
        await self.client.resolve(url)
        return create_SongDTO({"url": url})
