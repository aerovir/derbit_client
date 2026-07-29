from unittest.mock import AsyncMock, patch

import pytest
from sqlalchemy import select

from app.models import PriceRecord


@pytest.fixture
def mock_deribit_client():
    """Mock DeribitClient to return predefined prices."""
    with patch("app.tasks.fetch_prices.DeribitClient") as mock:
        client_instance = AsyncMock()
        client_instance.get_index_price = AsyncMock(side_effect=lambda name: {
            "btc_usd": 65000.0,
            "eth_usd": 3500.0,
        }.get(name, 0.0))
        mock.return_value = client_instance
        yield mock


@pytest.fixture(autouse=True)
def eager_mode():
    """Run Celery tasks synchronously in tests."""
    from app.tasks.celery_app import celery_app
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    yield
    celery_app.conf.task_always_eager = False
    celery_app.conf.task_eager_propagates = False


@pytest.mark.asyncio
async def test_fetch_prices_creates_records(mock_deribit_client, session) -> None:
    """fetch_prices должен создать записи в БД для каждого тикера."""
    from app.tasks.fetch_prices import fetch_prices

    result = fetch_prices.delay()
    task_result = result.get(timeout=5)

    assert task_result["status"] == "ok"
    assert task_result["fetched"] == 2

    # Verify DB records
    records_result = await session.execute(
        select(PriceRecord).order_by(PriceRecord.ticker)
    )
    records = records_result.scalars().all()

    assert len(records) == 2
    assert records[0].ticker == "btc_usd"
    assert records[0].price == 65000.0
    assert records[1].ticker == "eth_usd"
    assert records[1].price == 3500.0

    # Verify timestamps are set (UNIX timestamps, recent)
    import time
    now = int(time.time())
    for record in records:
        assert isinstance(record.timestamp, int)
        assert now - 10 <= record.timestamp <= now + 1


@pytest.mark.asyncio
async def test_fetch_prices_with_api_error(mock_deribit_client, session) -> None:
    """fetch_prices должен обрабатывать ошибки API для отдельных тикеров."""
    from app.client.deribit import DeribitAPIError
    mock_client = mock_deribit_client.return_value
    mock_client.get_index_price = AsyncMock(side_effect=[
        65000.0,  # btc_usd succeeds
        DeribitAPIError("Invalid params", code=-32602),  # eth_usd fails
    ])

    from app.tasks.fetch_prices import fetch_prices

    result = fetch_prices.delay()
    task_result = result.get(timeout=5)

    assert task_result["status"] == "partial"
    assert task_result["fetched"] == 1
    assert task_result["errors"] == 1

    # Only btc_usd should be saved
    records_result = await session.execute(select(PriceRecord))
    records = records_result.scalars().all()

    assert len(records) == 1
    assert records[0].ticker == "btc_usd"


@pytest.mark.asyncio
async def test_fetch_prices_all_fail(mock_deribit_client, session) -> None:
    """fetch_prices должен возвращать ошибку, если все тикеры не удались."""
    from app.client.deribit import DeribitAPIError
    mock_client = mock_deribit_client.return_value
    mock_client.get_index_price = AsyncMock(
        side_effect=DeribitAPIError("API error", code=-1)
    )

    from app.tasks.fetch_prices import fetch_prices

    result = fetch_prices.delay()
    task_result = result.get(timeout=5)

    assert task_result["status"] == "error"
    assert task_result["fetched"] == 0
    assert task_result["errors"] == 2
