from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL, DB_NAME, USE_SQLITE

if DATABASE_URL.startswith("mysql") and not USE_SQLITE:
    # Create the database if it does not exist before creating the engine.
    base_url = DATABASE_URL.rsplit("/", 1)[0] + "/"
    temp_engine = create_engine(base_url, future=True)
    with temp_engine.connect() as connection:
        connection.execute(text(f"CREATE DATABASE IF NOT EXISTS {DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
        connection.commit()
    temp_engine.dispose()

engine = create_engine(DATABASE_URL, future=True, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, future=True)
Base = declarative_base()

if DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _fk_pragma_on_connect(dbapi_con, connection_record):
        dbapi_con.execute('PRAGMA foreign_keys=ON')
