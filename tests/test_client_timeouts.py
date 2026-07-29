"""Tests for aiohttp timeout configuration in DeribitClient."""

import asyncio
from unittest.mock import patch

import pytest

from app.client.deribit import DeribitClient


@pytest.mark.asyncio
async def test_client_accepts_custom_timeout() -> None:
    """DeribitClient должен принимать timeout в конструкторе."""
    client = DeribitClient(base_url="https://test.deribit.com/api/v2", timeout=5)
    assert client._timeout == 5


@pytest.mark.asyncio
async def test_client_default_timeout() -> None:
    """DeribitClient должен иметь разумный timeout по умолчанию."""
    client = DeribitClient(base_url="https://test.deribit.com/api/v2")
    assert client._timeout == 10
    assert 5 <= client._timeout <= 30


@pytest.mark.asyncio
async def test_client_stores_timeout_as_float() -> None:
    """_timeout должен храниться как float/int."""
    client = DeribitClient(base_url="https://test.deribit.com/api/v2", timeout=7.5)
    assert isinstance(client._timeout, (int, float))
    assert client._timeout == 7.5


@pytest.mark.asyncio
async def test_timeout_raises_on_slow_request() -> None:
    """При превышении timeout должно возникать asyncio.TimeoutError."""
    client = DeribitClient(base_url="https://test.deribit.com/api/v2", timeout=0.001)

    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = asyncio.TimeoutError("Request timed out")

        with pytest.raises(asyncio.TimeoutError):
            await client.get_index_price("btc_usd")
