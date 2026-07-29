import pytest
import pytest_asyncio
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from sqlalchemy.pool import NullPool

from app.config import settings
from app.models import Base


@pytest_asyncio.fixture
async def engine():
    """Create a fresh engine per test function (NullPool to avoid connection reuse)."""
    eng = create_async_engine(settings.database_url, echo=False, poolclass=NullPool)
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield eng
    async with eng.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await eng.dispose()


@pytest_asyncio.fixture
async def session(engine):
    """Provide a clean session per test."""
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as s:
        yield s


@pytest.mark.asyncio
async def test_create_price_record(session) -> None:
    """PriceRecord создаётся и читается из БД."""
    from app.models import PriceRecord

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
    from app.models import PriceRecord

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
    from app.models import PriceRecord

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
    from app.models import PriceRecord

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
    from app.models import PriceRecord

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
    from app.models import PriceRecord

    record = PriceRecord(ticker="btc_usd", price=12345.67, timestamp=1)
    session.add(record)
    await session.commit()

    result = await session.get(PriceRecord, record.id)
    assert isinstance(result.price, float)
    assert result.price == 12345.67


@pytest.mark.asyncio
async def test_ticker_indexed(engine) -> None:
    """ticker должен иметь индекс для быстрого поиска."""
    from sqlalchemy import inspect

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
    from sqlalchemy import inspect

    async with engine.connect() as conn:
        indexes = await conn.run_sync(
            lambda sync_conn: inspect(sync_conn).get_indexes("price_records")
        )

    ts_indexes = [
        idx for idx in indexes
        if any(col == "timestamp" for col in idx["column_names"])
    ]
    assert len(ts_indexes) >= 1, "timestamp column should be indexed"
