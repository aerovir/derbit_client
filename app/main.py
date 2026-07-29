from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.api.health import router as health_router
from app.api.prices import router as prices_router
from app.database import init_db
from app.limiter import limiter


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database tables on startup."""
    await init_db()
    yield


app = FastAPI(title="Deribit Price API", version="1.0.0", lifespan=lifespan)

# Rate limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

# CORS — разрешены только GET методы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(prices_router)
