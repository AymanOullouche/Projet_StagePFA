import os
from pathlib import Path
from urllib.parse import quote_plus

DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "1234")
DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = os.getenv("DB_PORT", "3306")
DB_NAME = os.getenv("DB_NAME", "inspection_scolaire")
USE_SQLITE = os.getenv("USE_SQLITE", "0").lower() in ("1", "true", "yes")

if USE_SQLITE:
    SQLITE_PATH = Path(__file__).resolve().parent.parent / "inspection.db"
    DATABASE_URL = f"sqlite:///{SQLITE_PATH}"
else:
    user = quote_plus(DB_USER)
    password = quote_plus(DB_PASS)
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"mysql+mysqlconnector://{user}:{password}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    )

API_PREFIX = "/api"
