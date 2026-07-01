import os
from pathlib import Path
from urllib.parse import quote_plus
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent.parent / ".env")

# Par défaut : MySQL via XAMPP (phpMyAdmin)
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inspection_scolaire")
USE_SQLITE = True

if USE_SQLITE:
    SQLITE_PATH = Path(__file__).resolve().parent.parent / "inspection.db"
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
else:
    user = quote_plus(DB_USER)
    password = quote_plus(DB_PASS)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"mysql+pymysql://{user}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

API_PREFIX = "/api"

# Configuration pour le stockage des images
UPLOADS_DIR = Path(__file__).resolve().parent.parent / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
MAX_UPLOAD_SIZE = 50 * 1024 * 1024  # 50MB

# URL de base pour servir les images
BASE_URL = os.getenv("BASE_URL", "http://localhost:8000")
