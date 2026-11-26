from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str
    sql_echo: bool = False
    secret_key: str
    access_token_expire_minutes: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-args]
