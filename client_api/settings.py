import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

from infrastructure.openweather.settings import OpenWeatherSettings
from infrastructure.redis.settings import RedisSettings

BASE_DIR = Path(__file__).parent
ENV = os.getenv("ENV", "local")


class Settings(BaseSettings):
    redis: RedisSettings = RedisSettings()
    openweathermap: OpenWeatherSettings = OpenWeatherSettings()

    model_config = SettingsConfigDict(
        env_file=(f"{BASE_DIR}/.env", f"{BASE_DIR}/.env.{ENV}"),
        env_nested_delimiter="__",
        case_sensitive=False
    )


settings = Settings()
