"""Tests for ticker query parameter validation."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_async_session
from app.main import app


@pytest.fixture
async def client(session):
    async def override_session():
        yield session

    app.dependency_overrides[get_async_session] = override_session
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


VALID_TICKERS = [
    "btc_usd",
    "eth_usd",
    "btc_usdc",
    "eth_usdt",
    "sol_usd",
    "xrp_usdc",
    "ada_usdt",
    "btc_eurr",
    "1inch_usd",
    "1000pepe_usdc",
]

INVALID_TICKERS = [
    "",
    " ",
    "BTC_USD",
    "btc-usd",
    "btc usd",
    "btc/usd",
    "<script>alert(1)</script>",
    "btc_usd' OR '1'='1",
    "btc_usd; DROP TABLE price_records;",
    "../../../etc/passwd",
    "a" * 50,
    "btc_",
    "_usd",
    "btc_usd_extra",
    "' OR 1=1 --",
]


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", VALID_TICKERS)
async def test_valid_tickers_accepted(client, ticker) -> None:
    """Валидные тикеры должны проходить (200, даже если данных нет)."""
    response = await client.get("/api/v1/prices", params={"ticker": ticker})
    # 200 — если данных нет; 422 — если валидация не прошла
    assert response.status_code == 200, f"Ticker '{ticker}' should be valid, got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", INVALID_TICKERS)
async def test_invalid_tickers_rejected(client, ticker) -> None:
    """Невалидные тикеры должны возвращать 422."""
    response = await client.get("/api/v1/prices", params={"ticker": ticker})
    assert response.status_code == 422, f"Ticker '{ticker}' should be rejected, got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", VALID_TICKERS)
async def test_valid_tickers_last_price(client, ticker) -> None:
    """Валидные тикеры должны проходить на /prices/last."""
    response = await client.get("/api/v1/prices/last", params={"ticker": ticker})
    assert response.status_code in (200, 404), f"Ticker '{ticker}' got {response.status_code}"


@pytest.mark.asyncio
@pytest.mark.parametrize("ticker", INVALID_TICKERS)
async def test_invalid_tickers_rejected_last(client, ticker) -> None:
    """Невалидные тикеры должны возвращать 422 на /prices/last."""
    response = await client.get("/api/v1/prices/last", params={"ticker": ticker})
    assert response.status_code == 422, f"Ticker '{ticker}' should be rejected, got {response.status_code}"
