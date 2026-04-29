from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

    DB_USERNAME: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_DATABASE: str

    AWS_CHATGPT_API_URL: str
    AWS_CHATGPT_API_KEY: str

    WEATHER_API_KEY: str

    DISCORD_TOKEN: str

config = Config()