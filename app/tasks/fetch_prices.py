import asyncio
import threading
import time

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.client.deribit import DeribitClient
from app.config import settings
from app.models import PriceRecord
from app.tasks.celery_app import celery_app

_sync_engine = create_engine(settings.database_url_sync, echo=False, pool_pre_ping=True)


def _run_async(coro):
    """Run a coroutine synchronously in a separate thread with its own event loop.

    This avoids 'asyncio.run() cannot be called from a running event loop'
    errors when Celery runs eagerly in async tests.
    """
    result = []
    exception = []

    def _target():
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        try:
            result.append(new_loop.run_until_complete(coro))
        except Exception as e:
            exception.append(e)
        finally:
            new_loop.close()

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    thread.join()

    if exception:
        raise exception[0]
    return result[0]


def _save_price(ticker: str, price: float) -> None:
    """Save a price record to the database (sync)."""
    record = PriceRecord(
        ticker=ticker,
        price=price,
        timestamp=int(time.time()),
    )
    with Session(_sync_engine) as session:
        session.add(record)
        session.commit()


@celery_app.task(
    name="app.tasks.fetch_prices.fetch_prices",
    autoretry_for=(Exception,),
    max_retries=3,
    default_retry_delay=10,
)
def fetch_prices() -> dict:
    """Fetch current index prices for all configured tickers and save to DB."""
    client = DeribitClient(base_url=settings.deribit_api_url)
    fetched = 0
    errors = 0

    for ticker in settings.fetch_tickers:
        try:
            price = _run_async(client.get_index_price(ticker))
            _save_price(ticker, price)
            fetched += 1
        except Exception:
            errors += 1

    if errors == 0:
        status = "ok"
    elif fetched == 0:
        status = "error"
    else:
        status = "partial"

    return {
        "status": status,
        "fetched": fetched,
        "errors": errors,
    }
