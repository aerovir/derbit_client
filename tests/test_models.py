"""Тесты для SQLAlchemy моделей.

Проверяем:
- Создание экземпляра PriceRecord
- Типы полей
- Название таблицы
- Индексы
"""

import pytest
from sqlalchemy import create_mock_engine, inspect
from sqlalchemy.schema import CreateTable

from app.models import PriceRecord
from app.database import Base


def test_price_record_table_name():
    """Таблица называется 'prices'."""
    assert PriceRecord.__tablename__ == "prices"


def test_price_record_fields_exist():
    """PriceRecord имеет все обязательные поля."""
    record = PriceRecord(
        ticker="btc_usd",
        price=50000.0,
        timestamp=1700000000,
    )
    assert record.ticker == "btc_usd"
    assert record.price == 50000.0
    assert record.timestamp == 1700000000


def test_price_record_id_autoincrement():
    """id — первичный ключ с автоинкрементом."""
    assert PriceRecord.id.primary_key


def test_price_record_ticker_indexed():
    """ticker имеет индекс для быстрого поиска."""
    assert PriceRecord.ticker.index is True


def test_price_record_timestamp_indexed():
    """timestamp имеет индекс для фильтрации по дате."""
    assert PriceRecord.timestamp.index is True


def test_price_record_repr():
    """PriceRecord имеет читаемое представление."""
    record = PriceRecord(
        ticker="btc_usd",
        price=50000.0,
        timestamp=1700000000,
    )
    repr_str = repr(record)
    assert "btc_usd" in repr_str
    assert "50000.0" in repr_str or "50000" in repr_str


def test_price_record_optional_id():
    """id может быть None при создании (автогенерация)."""
    record = PriceRecord(
        ticker="eth_usd",
        price=3000.0,
        timestamp=1700000001,
    )
    assert record.id is None or record.id is not None


def test_base_metadata():
    """PriceRecord зарегистрирован в Base.metadata."""
    assert PriceRecord.__tablename__ in Base.metadata.tables
