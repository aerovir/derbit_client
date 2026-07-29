"""Tests for Celery configuration."""

from datetime import timedelta

from app.tasks.celery_app import celery_app


def _total_seconds(value):
    """Convert result_expires value to seconds."""
    if isinstance(value, timedelta):
        return value.total_seconds()
    return float(value)


def test_result_expires_is_set() -> None:
    """result_expires должен быть установлен, чтобы результаты задач не накапливались в БД."""
    assert "result_expires" in celery_app.conf
    expires = celery_app.conf.result_expires
    assert expires is not None
    seconds = _total_seconds(expires)
    assert seconds > 0


def test_result_expires_reasonable() -> None:
    """result_expires должен быть в разумном диапазоне (1-24 часа)."""
    expires = celery_app.conf.result_expires
    hours = _total_seconds(expires) / 3600
    assert 1 <= hours <= 24


def test_result_expires_configured_not_default() -> None:
    """result_expires должен быть явно переопределён, а не оставлен по умолчанию."""
    # Если бы defaults использовались, мы бы не писали этот тест
    expires = celery_app.conf.result_expires
    hours = _total_seconds(expires) / 3600
    # Убеждаемся что это не дефолт timedelta(days=1)=24ч, а явно меньше
    assert hours < 24, "Should be explicitly set to less than default 24h"
