from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str

    ANTHROPIC_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4.1-mini"
    ANTHROPIC_MODEL: str = "claude-haiku-4-5"

    WEATHER_API_KEY: str

    DISCORD_TOKEN: str

config = Config()