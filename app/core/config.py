from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import PostgresDsn, field_validator
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "test service"
    DEBUG: bool = False
    

    DATABASE_URL: PostgresDsn
    DB_ECHO: bool = False


    BANK_API_BASE_URL: str = "https://bank.api"
    BANK_API_TIMEOUT: float = 5.0


    LOG_LEVEL: str = "INFO"


    model_config = SettingsConfigDict(

        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("DATABASE_URL", mode="after")
    @classmethod
    def assemble_db_url(cls, v: PostgresDsn) -> str:
        """
        URL базы данных возвращается как строка.
        """
        return str(v)


settings = Settings()