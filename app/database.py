"""Database engine, session factory, and migration management."""

import subprocess
import sys
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.models import Base

engine = create_async_engine(settings.database_url, echo=False)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


def run_migrations() -> None:
    """Apply pending Alembic migrations using the sync DB URL."""
    from alembic.config import Config
    from alembic import command

    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", str(settings.database_url_sync))
    command.upgrade(alembic_cfg, "head")


async def init_db() -> None:
    """Apply database migrations on startup.

    Falls back to create_all if alembic is not configured
    (e.g. in test environment without alembic.ini).
    """
    import os

    if os.path.exists("alembic.ini") and os.path.isdir("alembic"):
        run_migrations()
    else:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency providing an async database session."""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
