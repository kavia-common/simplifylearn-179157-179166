from functools import lru_cache
from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.

    - DATABASE_URL: SQLAlchemy DB URL, defaults to SQLite file DB.
    - CORS_ORIGINS: Comma-separated list of allowed origins for CORS.
    """
    # Database config: default to SQLite file in project directory
    DATABASE_URL: str = Field(
        default="sqlite:///./app.db",
        description="SQLAlchemy database URL. Defaults to local SQLite file."
    )

    # CORS allowed origins: comma-separated list, default allow all
    CORS_ORIGINS: Optional[str] = Field(
        default="*",
        description="Comma-separated list of allowed CORS origins. Use '*' to allow all."
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


@lru_cache()
def get_settings() -> Settings:
    """
    Returns a cached Settings instance.
    """
    return Settings()
