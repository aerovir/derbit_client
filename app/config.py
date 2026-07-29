"""Конфигурация приложения.

Настройки загружаются из переменных окружения или .env файла.
Используется pydantic-settings для валидации и типизации.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения.

    Все значения могут быть переопределены через переменные окружения
    или .env файл в корне проекта.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # PostgreSQL
    DB_URL: str = "postgresql+asyncpg://derbit:derbit@localhost:5432/derbit"

    # Redis (для Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Deribit API
    DERIBIT_API_URL: str = "https://www.deribit.com/api/v2"

    # Список тикеров (через запятую)
    TICKERS: str = "btc_usd,eth_usd"

    # Интервал сбора цен в минутах
    FETCH_INTERVAL_MINUTES: int = 1

    @property
    def ticker_list(self) -> list[str]:
        """Возвращает список тикеров.

        Парсит строку TICKERS, разделённую запятыми, в список строк.
        """
        return [t.strip() for t in self.TICKERS.split(",") if t.strip()]


settings = Settings()
