from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.prices import router as prices_router
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    await init_db()
    yield


app = FastAPI(title="Deribit Price API", version="1.0.0", lifespan=lifespan)

app.include_router(prices_router)
