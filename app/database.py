"""Подключение к базе данных и управление сессиями.

Используется SQLAlchemy 2.0 asyncio для асинхронной работы с PostgreSQL.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


class Base(DeclarativeBase):
    """Базовый класс для всех SQLAlchemy моделей."""

    pass


engine = create_async_engine(
    settings.DB_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def init_db() -> None:
    """Создание всех таблиц в базе данных.

    Вызывается при старте приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Получение сессии для работы с БД.

    Используется как dependency в FastAPI.
    """
    async with async_session_factory() as session:
        yield session
