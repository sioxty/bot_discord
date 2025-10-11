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
    client = SoundCloud()
    result = await client.search("Imagine Dragons Believer")
    print(result[0].title)


if __name__ == "__main__":
    asyncio.run(main())
