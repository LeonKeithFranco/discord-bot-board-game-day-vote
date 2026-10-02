from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE_PATH = Path(__file__).resolve().parent.parent / ".env"


class _Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=_ENV_FILE_PATH,
        case_sensitive=True,
        env_file_encoding="utf-8",
        extra="forbid",
    )

    TOKEN: str = Field(min_length=1)
    SERVER_NAME: str = Field(min_length=1)
    CHANNEL_NAME: str = Field(min_length=1)
    THREAD_NAME: str = Field(min_length=1)
    ROLE_NAME: str = Field(min_length=1)
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"


settings = _Settings()
