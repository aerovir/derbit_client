"""Tests for pagination support in price list endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_async_session
from app.main import app
from app.models import PriceRecord


@pytest.fixture
async def client(session):
    async def override_session():
        yield session

    app.dependency_overrides[get_async_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def many_records(session):
    """Insert 50 sample records for pagination testing."""
    records = [
        PriceRecord(ticker="btc_usd", price=float(50000 + i), timestamp=1000000 + i)
        for i in range(50)
    ]
    session.add_all(records)
    await session.commit()


@pytest.mark.asyncio
async def test_default_limit(client, many_records) -> None:
    """без указания limit должны вернуться все записи (или дефолтный лимит)."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) <= 100
    assert len(data) == 50  # У нас 50 записей, должны вернуться все


@pytest.mark.asyncio
async def test_limit_param(client, many_records) -> None:
    """limit должен ограничивать количество записей."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd", "limit": 10})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10


@pytest.mark.asyncio
async def test_skip_param(client, many_records) -> None:
    """skip должен пропускать первые N записей."""
    response = await client.get(
        "/api/v1/prices", params={"ticker": "btc_usd", "skip": 10, "limit": 5}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    # Проверяем, что это записи с индекса 10-14
    assert data[0]["price"] == 50010.0
    assert data[-1]["price"] == 50014.0


@pytest.mark.asyncio
async def test_skip_without_limit(client, many_records) -> None:
    """skip без limit должен работать (используется дефолтный limit)."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd", "skip": 45})
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5  # Осталось 5 записей


@pytest.mark.asyncio
async def test_limit_max(client, many_records) -> None:
    """limit не должен превышать максимальное значение (1000)."""
    response = await client.get(
        "/api/v1/prices", params={"ticker": "btc_usd", "limit": 9999}
    )
    assert response.status_code == 200
    data = response.json()
    # Должно быть не больше 1000, у нас всего 50
    assert len(data) == 50


@pytest.mark.asyncio
async def test_limit_negative(client) -> None:
    """отрицательный limit должен возвращать 422."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd", "limit": -1})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_skip_negative(client) -> None:
    """отрицательный skip должен возвращать 422."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd", "skip": -1})
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_pagination_offset_correct(client, many_records) -> None:
    """Проверка правильности offset: page 1 и page 2 не должны пересекаться."""
    response1 = await client.get(
        "/api/v1/prices", params={"ticker": "btc_usd", "skip": 0, "limit": 10}
    )
    response2 = await client.get(
        "/api/v1/prices", params={"ticker": "btc_usd", "skip": 10, "limit": 10}
    )
    data1 = response1.json()
    data2 = response2.json()

    ids1 = {r["id"] for r in data1}
    ids2 = {r["id"] for r in data2}
    assert len(ids1 & ids2) == 0  # Пересечений быть не должно
