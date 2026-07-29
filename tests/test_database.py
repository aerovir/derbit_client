"""Тесты для подключения к базе данных.

Проверяем:
- Создание async engine
- Создание sessionmaker
- Функцию get_session
"""

import pytest
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from app.database import engine, async_session_factory, get_session


def test_engine_is_async():
    """engine — асинхронный SQLAlchemy Engine."""
    assert isinstance(engine, AsyncEngine)


def test_engine_url_contains_postgresql():
    """engine использует PostgreSQL."""
    assert "postgresql" in engine.url.drivername


def test_session_factory_is_async():
    """session_factory создаёт AsyncSession."""
    assert isinstance(async_session_factory, async_sessionmaker)
    assert async_session_factory.class_ is AsyncSession


@pytest.mark.asyncio
async def test_get_session_yields_async_session():
    """get_session — асинхронный генератор, возвращающий AsyncSession."""
    async for session in get_session():
        assert isinstance(session, AsyncSession)
        break
