import os
from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / ".env")

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-only-change-this-secret-before-deploying")
    DATABASE = str(ROOT / "data" / "store.db")
    UPLOAD_FOLDER = str(ROOT / "static" / "uploads")
    ADMIN_NAME = os.getenv("ADMIN_NAME", "sashath")
    ADMIN_NUMBER = os.getenv("ADMIN_NUMBER", "7412580963")
    ADMIN_CODE = os.getenv("ADMIN_CODE", "71606")
    MAX_CONTENT_LENGTH = 7 * 1024 * 1024
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 30
    SESSION_REFRESH_EACH_REQUEST = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    SESSION_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "0") == "1"
