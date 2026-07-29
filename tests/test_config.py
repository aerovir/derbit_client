"""Тесты для конфигурации приложения.

Проверяем:
- Загрузку значений по умолчанию
- Переопределение через переменные окружения
- Парсинг списка тикеров
"""

import os
from unittest.mock import patch

import pytest

from app.config import Settings


def test_default_tickers():
    """По умолчанию TICKERS содержит BTC и ETH."""
    settings = Settings()
    assert "btc_usd" in settings.ticker_list
    assert "eth_usd" in settings.ticker_list


def test_default_api_url():
    """По умолчанию DERIBIT_API_URL корректный."""
    settings = Settings()
    assert "deribit.com" in settings.DERIBIT_API_URL


def test_default_fetch_interval():
    """По умолчанию FETCH_INTERVAL_MINUTES = 1."""
    settings = Settings()
    assert settings.FETCH_INTERVAL_MINUTES == 1


def test_ticker_list_is_list():
    """ticker_list возвращает list[str]."""
    settings = Settings()
    assert isinstance(settings.ticker_list, list)
    assert all(isinstance(t, str) for t in settings.ticker_list)


@pytest.mark.parametrize("env_value,expected", [
    ("btc_usd", ["btc_usd"]),
    ("btc_usd,eth_usd,sol_usd", ["btc_usd", "eth_usd", "sol_usd"]),
    (" ETH_USD , BTC_USD ", ["ETH_USD", "BTC_USD"]),
])
def test_tickers_parsing(env_value, expected):
    """TICKERS парсятся из строки с разделением запятой."""
    with patch.dict(os.environ, {"TICKERS": env_value}, clear=True):
        settings = Settings()
        assert settings.ticker_list == expected


def test_db_url_default():
    """DB_URL имеет значение по умолчанию."""
    settings = Settings()
    assert "postgresql" in settings.DB_URL


def test_redis_url_default():
    """REDIS_URL имеет значение по умолчанию."""
    settings = Settings()
    assert "redis" in settings.REDIS_URL


def test_custom_env_overrides():
    """Переменные окружения переопределяют значения по умолчанию."""
    env_vars = {
        "DB_URL": "postgresql+asyncpg://custom:pass@host:5432/testdb",
        "REDIS_URL": "redis://custom:6379/1",
        "DERIBIT_API_URL": "https://test.deribit.com/api/v2",
        "FETCH_INTERVAL_MINUTES": "5",
    }
    with patch.dict(os.environ, env_vars, clear=True):
        settings = Settings()
        assert settings.DB_URL == env_vars["DB_URL"]
        assert settings.REDIS_URL == env_vars["REDIS_URL"]
        assert settings.DERIBIT_API_URL == env_vars["DERIBIT_API_URL"]
        assert settings.FETCH_INTERVAL_MINUTES == 5
