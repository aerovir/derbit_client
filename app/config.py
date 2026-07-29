"""Конфигурация приложения.

Настройки загружаются из переменных окружения или .env файла.
"""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
