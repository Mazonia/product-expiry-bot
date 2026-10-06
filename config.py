"""
Configuration for Instant Bill & Expiry Date Alert Bot
"""

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
DAILY_CHECK_TIME = os.getenv("DAILY_CHECK_TIME", "08:00").strip()

RAW_AUTHORIZED_IDS = os.getenv("AUTHORIZED_USER_IDS", "0").strip()
AUTHORIZED_USER_IDS: set[int] = set()
for item in RAW_AUTHORIZED_IDS.split(","):
    item = item.strip()
    if item and item.isdigit() and int(item) != 0:
        AUTHORIZED_USER_IDS.add(int(item))

UPLOADS_DIR = BASE_DIR / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = BASE_DIR / "expiry_tracker.db"
