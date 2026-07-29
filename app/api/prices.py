from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_async_session
from app.models import PriceRecord
from app.schemas import PriceLastResponse, PriceResponse

router = APIRouter(prefix="/api/v1/prices", tags=["prices"])


@router.get("", response_model=list[PriceResponse])
async def get_prices(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    date_from: int | None = Query(None, description="Start UNIX timestamp"),
    date_to: int | None = Query(None, description="End UNIX timestamp"),
    session: AsyncSession = Depends(get_async_session),
) -> list[PriceRecord]:
    """Get all price records for a ticker, optionally filtered by date range."""
    query = (
        select(PriceRecord)
        .where(PriceRecord.ticker == ticker)
        .order_by(PriceRecord.timestamp)
    )

    if date_from is not None:
        query = query.where(PriceRecord.timestamp >= date_from)
    if date_to is not None:
        query = query.where(PriceRecord.timestamp <= date_to)

    result = await session.execute(query)
    return list(result.scalars().all())


@router.get("/last", response_model=PriceLastResponse)
async def get_last_price(
    ticker: str = Query(..., description="Currency ticker, e.g. btc_usd"),
    session: AsyncSession = Depends(get_async_session),
) -> PriceRecord:
    """Get the most recent price record for a ticker."""
    query = (
        select(PriceRecord)
        .where(PriceRecord.ticker == ticker)
        .order_by(PriceRecord.timestamp.desc())
        .limit(1)
    )
    result = await session.execute(query)
    record = result.scalar_one_or_none()
    if record is None:
        raise HTTPException(status_code=404, detail="No price data found")
    return record
