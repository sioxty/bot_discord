import dotenv

dotenv.load_dotenv()

TOKEN = dotenv.get_key(".env", "TOKEN")
CLIENT_ID = dotenv.get_key(".env", "CLIENT_ID")
FFMPEG_PATH=dotenv.get_key('.env','FFMPEG_PATH')