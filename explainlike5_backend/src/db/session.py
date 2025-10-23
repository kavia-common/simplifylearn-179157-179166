from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.core.config import get_settings

settings = get_settings()

# Determine if we are using SQLite to set appropriate connect args
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Create the SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if is_sqlite else {},
    future=True,
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,
)

# PUBLIC_INTERFACE
def get_db() -> Generator:
    """Yield a SQLAlchemy Session and ensure it is closed after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
