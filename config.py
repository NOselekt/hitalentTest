from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).parent
DB_USER = "postgres"
DB_PASS = "uriel999"
DB_NAME = "hitalentTest"
DB_HOST = "localhost"
DB_PORT = "5432"


class Settings(BaseSettings):
    """Central application configuration."""

    db_user: str = Field(default=DB_USER, alias="DB_USER")
    db_password: str = Field(default=DB_PASS, alias="DB_PASS")
    db_name: str = Field(default=DB_NAME, alias="DB_NAME")
    db_host: str = Field(default=DB_HOST, alias="DB_HOST")
    db_port: int = Field(default=DB_PORT, alias="DB_PORT")
    db_echo: bool = Field(default=False, alias="DB_ECHO")

    def _build_db_url(self, driver: str) -> str:
        return (
            f"{driver}://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def async_database_url(self) -> str:
        return self._build_db_url("postgresql+asyncpg")

    @property
    def sync_database_url(self) -> str:
        return self._build_db_url("postgresql+psycopg2")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
