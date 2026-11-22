# config.py - all settings in one place
# Values are read from the .env file in the project folder.

import os
import secrets
from pathlib import Path
from dotenv import load_dotenv

# Project root folder (the folder that contains backend/ and frontend/)
BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")

# ---------- Database ----------
# MySQL example : mysql+pymysql://root:password@localhost:3306/visionstock
# Quick test    : sqlite:///visionstock.db   (no MySQL needed)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:password@localhost:3306/visionstock"
)

# ---------- Login (JWT token) ----------
# The secret key signs the login tokens. If anyone knows it, they can make a
# fake token. So we never use a fixed default key:
#   1. If you set SECRET_KEY in .env (a long random text), we use it.
#   2. Otherwise we make a random key once and keep it in the file ".secret_key"
#      (this file is in .gitignore, never upload it).
PLACEHOLDER_KEYS = ("", "change-this-to-a-long-random-text", "change-this-secret-key")


def get_secret_key():
    key = os.getenv("SECRET_KEY", "").strip()
    if key and not key.startswith(PLACEHOLDER_KEYS[1]) and key != PLACEHOLDER_KEYS[2]:
        return key

    key_file = BASE_DIR / ".secret_key"
    if key_file.exists():
        saved = key_file.read_text().strip()
        if saved:
            return saved

    new_key = secrets.token_hex(32)
    key_file.write_text(new_key)
    return new_key


SECRET_KEY = get_secret_key()
TOKEN_HOURS = int(os.getenv("TOKEN_HOURS", "8"))

# ---------- Computer vision ----------
FRONTEND_DIR = BASE_DIR / "frontend"
VIDEO_FOLDER = BASE_DIR / "videos"
CUSTOM_MODEL = BASE_DIR / "models" / "best.pt"
# If models/best.pt is not there, a small pretrained YOLO model is used
MODEL_PATH = str(CUSTOM_MODEL) if CUSTOM_MODEL.exists() else "yolov8n.pt"
CONFIDENCE = float(os.getenv("CONFIDENCE", "0.4"))
SAVE_INTERVAL = float(os.getenv("SAVE_INTERVAL", "5"))   # seconds between database updates
FRAME_WIDTH = int(os.getenv("FRAME_WIDTH", "960"))       # frames are resized to this width

# ---------- Kafka (optional, advanced) ----------
KAFKA_ENABLED = os.getenv("KAFKA_ENABLED", "false").lower() == "true"
KAFKA_SERVER = os.getenv("KAFKA_SERVER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "inventory-events")
