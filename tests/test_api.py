import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_async_session
from app.main import app
from app.models import PriceRecord


@pytest.fixture
async def client(session):
    """Override DB dependency with test session."""

    async def override_session():
        yield session

    app.dependency_overrides[get_async_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest.fixture
async def seed_data(session):
    """Insert sample price records for testing."""
    records = [
        PriceRecord(ticker="btc_usd", price=50000.0, timestamp=1000000),
        PriceRecord(ticker="btc_usd", price=51000.0, timestamp=2000000),
        PriceRecord(ticker="btc_usd", price=52000.0, timestamp=3000000),
        PriceRecord(ticker="eth_usd", price=4000.0, timestamp=1000000),
    ]
    session.add_all(records)
    await session.commit()


@pytest.mark.asyncio
async def test_get_all_prices(client, seed_data) -> None:
    """GET /api/v1/prices?ticker=btc_usd — все записи для ticker."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert all(r["ticker"] == "btc_usd" for r in data)
    assert data[0]["price"] == 50000.0
    assert data[-1]["price"] == 52000.0


@pytest.mark.asyncio
async def test_get_last_price(client, seed_data) -> None:
    """GET /api/v1/prices/last?ticker=btc_usd — последняя запись."""
    response = await client.get("/api/v1/prices/last", params={"ticker": "btc_usd"})

    assert response.status_code == 200
    data = response.json()
    assert data["ticker"] == "btc_usd"
    assert data["price"] == 52000.0
    assert data["timestamp"] == 3000000


@pytest.mark.asyncio
async def test_get_prices_with_date_filter(client, seed_data) -> None:
    """GET /api/v1/prices?ticker=btc_usd&date_from=...&date_to=... — фильтр по дате."""
    response = await client.get(
        "/api/v1/prices",
        params={"ticker": "btc_usd", "date_from": 1500000, "date_to": 2500000},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["price"] == 51000.0
    assert data[0]["timestamp"] == 2000000


@pytest.mark.asyncio
async def test_get_prices_with_date_from_only(client, seed_data) -> None:
    """Фильтр только с date_from (без date_to) должен работать."""
    response = await client.get(
        "/api/v1/prices",
        params={"ticker": "btc_usd", "date_from": 2000000},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["timestamp"] == 2000000
    assert data[1]["timestamp"] == 3000000


@pytest.mark.asyncio
async def test_get_prices_with_date_to_only(client, seed_data) -> None:
    """Фильтр только с date_to (без date_from) должен работать."""
    response = await client.get(
        "/api/v1/prices",
        params={"ticker": "btc_usd", "date_to": 2000000},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["timestamp"] == 1000000
    assert data[1]["timestamp"] == 2000000


@pytest.mark.asyncio
async def test_get_last_price_empty(client) -> None:
    """GET /api/v1/prices/last для пустой таблицы — 404."""
    response = await client.get("/api/v1/prices/last", params={"ticker": "btc_usd"})

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_get_prices_empty_ticker(client, seed_data) -> None:
    """GET /api/v1/prices для ticker без данных — пустой список."""
    response = await client.get("/api/v1/prices", params={"ticker": "sol_usd"})

    assert response.status_code == 200
    data = response.json()
    assert data == []


@pytest.mark.asyncio
async def test_missing_ticker_param(client) -> None:
    """Запрос без обязательного ticker — 422."""
    response = await client.get("/api/v1/prices")
    assert response.status_code == 422

    response = await client.get("/api/v1/prices/last")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_all_prices_ordered(client, seed_data) -> None:
    """Все записи должны быть отсортированы по timestamp."""
    response = await client.get("/api/v1/prices", params={"ticker": "btc_usd"})

    data = response.json()
    timestamps = [r["timestamp"] for r in data]
    assert timestamps == sorted(timestamps)
