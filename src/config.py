import os
from functools import lru_cache
from pathlib import Path
from typing import Literal
from urllib.parse import quote, quote_plus

from dotenv import find_dotenv, load_dotenv
from pydantic import BaseModel, PostgresDsn, SecretStr, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv(find_dotenv())


def read_password(name: Literal["pg_password", "rabbitmq_password"]) -> str | None:
    """Read a secret value from Docker secrets or a local fallback file.

    Args:
        name: Secret name without file extension.

    Returns:
        Secret value if a matching file exists, otherwise `None`.
    """

    docker_secret = Path(f"/run/secrets/{name}")
    if docker_secret.exists():
        return docker_secret.read_text(encoding="utf-8").strip()

    local_secret = Path(f"./secrets/{name}.txt")
    if local_secret.exists():
        return local_secret.read_text(encoding="utf-8").strip()

    return None


class DBSettings(BaseModel):
    """Database connection settings."""

    user: str
    password: str = os.getenv("DATABASE__PASSWORD") or read_password("pg_password") or ""
    name: str
    host: str
    port: int

    echo: bool

    pool_size: int
    pool_pre_ping: bool

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """Build the async SQLAlchemy database URL."""

        encoded_user = quote_plus(self.user)

        encoded_password = quote_plus(self.password)

        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=encoded_user,
            password=encoded_password,
            host=self.host,
            port=self.port,
            path=self.name,
        ).encoded_string()


class MsgBrSettings(BaseModel):
    """Message broker connection settings."""

    user: str
    password: str = os.getenv("BROKER__PASSWORD") or read_password("rabbitmq_password") or ""
    host: str
    port: int
    vhost: str

    @computed_field  # type: ignore[prop-decorator]
    @property
    def url(self) -> str:
        """Build the broker URL."""

        encoded_user = quote(self.user)

        encoded_password = quote(self.password)

        return f"amqp://{encoded_user}:{encoded_password}@{self.host}:{self.port}/{self.vhost}"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    log_level: str = "INFO"

    # DB
    database: DBSettings

    # Message Broker
    broker: MsgBrSettings

    app_api_key: SecretStr = SecretStr("secret-key")


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    return Settings()  # pyright: ignore[reportCallIssue]


settings = get_settings()
