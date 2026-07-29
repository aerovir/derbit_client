from celery import Celery

from app.config import settings

celery_app = Celery(
    "deribit",
    broker="sqla+postgresql://deribit:deribit@db:5432/deribit",
    backend="db+postgresql://deribit:deribit@db:5432/deribit",
    include=["app.tasks.fetch_prices"],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "fetch-prices-every-minute": {
            "task": "app.tasks.fetch_prices.fetch_prices",
            "schedule": 60.0,
        },
    },
)
