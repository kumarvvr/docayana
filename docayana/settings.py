from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """App config, read from DOCAYANA_* env vars or a .env file in the working directory."""

    model_config = SettingsConfigDict(
        env_prefix="DOCAYANA_", env_file=".env", extra="ignore"
    )

    gcp_creds: Path
    firestore_database: str = "(default)"
