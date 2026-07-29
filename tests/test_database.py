import pytest
from sqlalchemy import inspect, select

from app.models import PriceRecord


@pytest.mark.asyncio
async def test_create_price_record(session) -> None:
    """PriceRecord создаётся и читается из БД."""
    record = PriceRecord(
        ticker="btc_usd",
        price=64488.96,
        timestamp=1700000000,
    )
    session.add(record)
    await session.commit()

    result = await session.get(PriceRecord, record.id)
    assert result is not None
    assert result.ticker == "btc_usd"
    assert result.price == 64488.96
    assert result.timestamp == 1700000000


@pytest.mark.asyncio
async def test_price_record_auto_increment_id(session) -> None:
    """PriceRecord.id должен автоинкрементиться."""
    r1 = PriceRecord(ticker="btc_usd", price=100.0, timestamp=1)
    r2 = PriceRecord(ticker="btc_usd", price=200.0, timestamp=2)
    session.add_all([r1, r2])
    await session.commit()

    assert r1.id is not None
    assert r2.id is not None
    assert r2.id > r1.id


@pytest.mark.asyncio
async def test_query_by_ticker(session) -> None:
    """Должна быть возможность найти записи по ticker."""
    session.add_all([
        PriceRecord(ticker="btc_usd", price=100.0, timestamp=1),
        PriceRecord(ticker="btc_usd", price=200.0, timestamp=2),
        PriceRecord(ticker="eth_usd", price=300.0, timestamp=3),
    ])
    await session.commit()

    result = await session.execute(
        select(PriceRecord).where(PriceRecord.ticker == "btc_usd")
    )
    records = result.scalars().all()

    assert len(records) == 2
    assert all(r.ticker == "btc_usd" for r in records)


@pytest.mark.asyncio
async def test_query_by_timestamp_range(session) -> None:
    """Должна быть возможность фильтрации по timestamp (date_from/date_to)."""
    session.add_all([
        PriceRecord(ticker="btc_usd", price=100.0, timestamp=100),
        PriceRecord(ticker="btc_usd", price=200.0, timestamp=200),
        PriceRecord(ticker="btc_usd", price=300.0, timestamp=300),
        PriceRecord(ticker="btc_usd", price=400.0, timestamp=400),
    ])
    await session.commit()

    result = await session.execute(
        select(PriceRecord)
        .where(PriceRecord.ticker == "btc_usd")
        .where(PriceRecord.timestamp >= 150)
        .where(PriceRecord.timestamp <= 350)
        .order_by(PriceRecord.timestamp)
    )
    records = result.scalars().all()

    assert len(records) == 2
    assert records[0].timestamp == 200
    assert records[1].timestamp == 300


@pytest.mark.asyncio
async def test_query_last_by_ticker(session) -> None:
    """Должна быть возможность получить последнюю запись по ticker (макс timestamp)."""
    session.add_all([
        PriceRecord(ticker="btc_usd", price=100.0, timestamp=100),
        PriceRecord(ticker="btc_usd", price=200.0, timestamp=300),
        PriceRecord(ticker="btc_usd", price=300.0, timestamp=200),
    ])
    await session.commit()

    result = await session.execute(
        select(PriceRecord)
        .where(PriceRecord.ticker == "btc_usd")
        .order_by(PriceRecord.timestamp.desc())
        .limit(1)
    )
    record = result.scalar_one()

    assert record.timestamp == 300
    assert record.price == 200.0


@pytest.mark.asyncio
async def test_price_stores_as_float(session) -> None:
    """price должен храниться и возвращаться как float."""
    record = PriceRecord(ticker="btc_usd", price=12345.67, timestamp=1)
    session.add(record)
    await session.commit()

    result = await session.get(PriceRecord, record.id)
    assert isinstance(result.price, float)
    assert result.price == 12345.67


@pytest.mark.asyncio
async def test_ticker_indexed(engine) -> None:
    """ticker должен иметь индекс для быстрого поиска."""
    async with engine.connect() as conn:
        indexes = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_indexes("price_records")
        )

    ticker_indexes = [
        idx for idx in indexes
        if any(col == "ticker" for col in idx["column_names"])
    ]
    assert len(ticker_indexes) >= 1, "ticker column should be indexed"


@pytest.mark.asyncio
async def test_timestamp_indexed(engine) -> None:
    """timestamp должен иметь индекс для быстрого поиска по датам."""
    async with engine.connect() as conn:
        indexes = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_indexes("price_records")
        )

    ts_indexes = [
        idx for idx in indexes
        if any(col == "timestamp" for col in idx["column_names"])
    ]
    assert len(ts_indexes) >= 1, "timestamp column should be indexed"
