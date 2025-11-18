from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).parent
db_user = "postgres"
db_password = "postgres"
db_name = "hitalentTest"
db_host = "pg"
db_port = 5432


class Settings(BaseSettings):
    """Central application configuration."""

    db_user: str = Field(default=db_user, alias="DB_USER")
    db_password: str = Field(default=db_password, alias="DB_PASS")
    db_name: str = Field(default=db_name, alias="DB_NAME")
    db_host: str = Field(default=db_host, alias="DB_HOST")
    db_port: int = Field(default=db_port, alias="DB_PORT")
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


settings = Settings()
