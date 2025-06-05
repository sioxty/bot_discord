import dotenv
import os

dotenv.load_dotenv()

TOKEN = os.getenv("TOKEN")
CLIENT_ID: str = os.getenv("CLIENT_ID")  # type: ignore
uri: str = os.getenv("URI")  # type: ignore
name_database = "bot_discord"
