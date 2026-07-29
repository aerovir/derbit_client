"""Health check endpoints for container orchestration probes."""

import time

from fastapi import APIRouter
from sqlalchemy import text

from app.database import async_session_factory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health() -> dict:
    """Liveness probe — всегда 200, если сервер жив."""
    return {"status": "ok"}


@router.get("/readyz")
async def readyz() -> dict:
    """Readiness probe — проверяет доступность БД."""
    db_status = "ok"
    try:
        async with async_session_factory() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    return {
        "database": db_status,
        "timestamp": int(time.time()),
    }
