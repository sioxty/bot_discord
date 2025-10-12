import dotenv
import os

from aiosoundcloud.soundcloud_client_dto import SoundCloud

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_ID: str = os.getenv("CLIENT_ID")  # type: ignore
LIMIT_QUEUE: int = int(os.getenv("LIMIT_QUEUE", 20))  # type: ignore
uri: str = os.getenv("URI")  # type: ignore
name_database = os.getenv("NAME_DATABASE", "bot_discord")

api = SoundCloud(client_id=CLIENT_ID)
