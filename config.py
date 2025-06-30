# config.py
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")
SESSION_NAME = os.getenv("SESSION_NAME", "anon")

# Telegram
SUPERGROUP_ID = int(os.getenv("SUPERGROUP_ID"))
TOPIC_ID = int(os.getenv("TOPIC_ID"))

# Пути
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LINKS_PATH = os.path.join(BASE_DIR, "links.txt")
TEMP_DIR = os.path.join(BASE_DIR, "temp_videos")
