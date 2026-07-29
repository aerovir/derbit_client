"""Tests for structured logging and request ID middleware."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_response_has_request_id(client) -> None:
    """Каждый ответ должен содержать X-Request-ID заголовок."""
    response = await client.get("/health")
    assert "X-Request-ID" in response.headers
    rid = response.headers["X-Request-ID"]
    assert len(rid) > 0
    assert isinstance(rid, str)


@pytest.mark.asyncio
async def test_request_id_unique_per_request(client) -> None:
    """Каждый запрос должен получать уникальный X-Request-ID."""
    r1 = await client.get("/health")
    r2 = await client.get("/health")
    assert r1.headers["X-Request-ID"] != r2.headers["X-Request-ID"]


@pytest.mark.asyncio
async def test_request_id_is_uuid(client) -> None:
    """X-Request-ID должен быть в формате UUID."""
    import uuid

    response = await client.get("/health")
    rid = response.headers["X-Request-ID"]
    assert isinstance(uuid.UUID(rid), uuid.UUID)  # не выбросит исключение


@pytest.mark.asyncio
async def test_request_id_persistent_on_error(client) -> None:
    """Даже при 422 ошибке должен быть X-Request-ID."""
    response = await client.get("/api/v1/prices", params={"ticker": "INVALID"})
    assert "X-Request-ID" in response.headers
    assert response.status_code == 422
