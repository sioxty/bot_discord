import dotenv
import os

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_ID: str = ""
LIMIT_QUEUE: int = int(os.getenv("LIMIT_QUEUE", 25))  # type: ignore
uri: str = os.getenv("URI")  # type: ignore
name_database = "bot_discord"
