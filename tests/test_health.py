"""Tests for health check endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health_returns_200(client) -> None:
    """GET /health должен возвращать 200."""
    response = await client.get("/health")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_health_returns_json(client) -> None:
    """GET /health должен возвращать JSON с статусом."""
    response = await client.get("/health")
    data = response.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_readyz_returns_200(client) -> None:
    """GET /readyz должен возвращать 200 при работающей БД."""
    response = await client.get("/readyz")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_readyz_contains_db_status(client) -> None:
    """GET /readyz должен содержать статус БД."""
    response = await client.get("/readyz")
    data = response.json()
    assert "database" in data
    assert data["database"] in ("ok", "error"), f"Unexpected db status: {data['database']}"
    if data["database"] == "error":
        pytest.skip("DB not available in this test environment")


@pytest.mark.asyncio
async def test_readyz_returns_timestamp(client) -> None:
    """GET /readyz должен содержать timestamp."""
    response = await client.get("/readyz")
    data = response.json()
    assert "timestamp" in data
    assert isinstance(data["timestamp"], (int, float))
