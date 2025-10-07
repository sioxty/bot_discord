import asyncio
from pprint import pprint

from aiosoundcloud import SoundCloud, SoundCloudClient
from config import CLIENT_ID
import logging

log = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main():
    client = SoundCloud(client_id=CLIENT_ID)
    result = await client.get_playlist(
        "https://soundcloud.com/maksim-slushayev/sets/playstyle", limit=10
    )
    print(result.title)


if __name__ == "__main__":
    asyncio.run(main())
