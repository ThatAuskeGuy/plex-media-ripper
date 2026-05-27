from dotenv import load_dotenv
import os

load_dotenv()

PLEX_MEDIA_ROOT = os.getenv("PLEX_MEDIA_ROOT", "/media/plex")
PLEX_URL = os.getenv("PLEX_URL", "http://localhost:32400")
PLEX_TOKEN = os.getenv("PLEX_TOKEN")
CD_DEVICE = os.getenv("CD_DEVICE", "/dev/sr0")
TEMP_RIP_DIR = os.getenv("TEMP_RIP_DIR", "/tmp/media_rip")