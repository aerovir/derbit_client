from unittest.mock import AsyncMock, MagicMock, patch

import aiohttp
import pytest

from app.client.deribit import DeribitClient, DeribitAPIError


@pytest.fixture
def client() -> DeribitClient:
    return DeribitClient(base_url="https://test.deribit.com/api/v2")


@pytest.fixture
def mock_response() -> dict:
    return {
        "jsonrpc": "2.0",
        "result": {
            "estimated_delivery_price": 64488.96,
            "index_price": 64488.96,
        },
        "usIn": 1785318624508188,
        "usOut": 1785318624508461,
        "usDiff": 273,
        "testnet": True,
    }


def _make_mock_get(json_data: dict, status: int = 200) -> MagicMock:
    """Create a mock for aiohttp.ClientSession.get that returns the given JSON."""
    mock_resp = MagicMock()
    mock_resp.__aenter__.return_value = mock_resp
    mock_resp.status = status
    mock_resp.json = AsyncMock(return_value=json_data)
    if status >= 400:
        mock_resp.raise_for_status.side_effect = aiohttp.ClientResponseError(
            request_info=MagicMock(),
            history=(),
            status=status,
            message="Error",
        )
    mock_get = MagicMock()
    mock_get.return_value = mock_resp
    return mock_get


@pytest.mark.asyncio
async def test_get_index_price_returns_float(client: DeribitClient, mock_response: dict) -> None:
    """get_index_price должна возвращать float значение index_price."""
    with patch("aiohttp.ClientSession.get", _make_mock_get(mock_response)):
        price = await client.get_index_price("btc_usd")

    assert isinstance(price, float)
    assert price == 64488.96


@pytest.mark.asyncio
async def test_get_index_price_sends_correct_request(client: DeribitClient, mock_response: dict) -> None:
    """get_index_price должна отправлять GET на правильный URL с правильным параметром."""
    mock_get = _make_mock_get(mock_response)
    with patch("aiohttp.ClientSession.get", mock_get):
        await client.get_index_price("eth_usd")

    mock_get.assert_called_once_with(
        "https://test.deribit.com/api/v2/public/get_index_price",
        params={"index_name": "eth_usd"},
    )


@pytest.mark.asyncio
async def test_get_index_price_raises_on_invalid_index(client: DeribitClient) -> None:
    """get_index_price должна поднимать DeribitAPIError при неверном index_name."""
    error_response = {
        "jsonrpc": "2.0",
        "error": {
            "code": -32602,
            "data": {"reason": "invalid index", "param": "index_name"},
            "message": "Invalid params",
        },
        "testnet": True,
        "usIn": 1785318741826156,
        "usOut": 1785318741826287,
        "usDiff": 131,
    }

    with patch("aiohttp.ClientSession.get", _make_mock_get(error_response)):
        with pytest.raises(DeribitAPIError) as exc_info:
            await client.get_index_price("invalid_ticker")

    assert "Invalid params" in str(exc_info.value)
    assert exc_info.value.code == -32602


@pytest.mark.asyncio
async def test_get_index_price_raises_on_http_error(client: DeribitClient) -> None:
    """get_index_price должна поднимать исключение при HTTP ошибке."""
    with patch("aiohttp.ClientSession.get", _make_mock_get({}, status=503)):
        with pytest.raises(aiohttp.ClientResponseError):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_raises_on_network_error(client: DeribitClient) -> None:
    """get_index_price должна поднимать исключение при сетевой ошибке."""
    with patch("aiohttp.ClientSession.get") as mock_get:
        mock_get.side_effect = aiohttp.ClientConnectionError("Connection refused")

        with pytest.raises(aiohttp.ClientConnectionError):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_missing_result_key(client: DeribitClient) -> None:
    """get_index_price должна поднимать DeribitAPIError, если в ответе нет result."""
    bad_response = {
        "jsonrpc": "2.0",
        "testnet": True,
    }

    with patch("aiohttp.ClientSession.get", _make_mock_get(bad_response)):
        with pytest.raises(DeribitAPIError, match="missing 'result'"):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_get_index_price_missing_index_price_key(client: DeribitClient) -> None:
    """get_index_price должна поднимать DeribitAPIError, если в result нет index_price."""
    bad_response = {
        "jsonrpc": "2.0",
        "result": {"estimated_delivery_price": 64488.96},
        "testnet": True,
    }

    with patch("aiohttp.ClientSession.get", _make_mock_get(bad_response)):
        with pytest.raises(DeribitAPIError, match="missing 'index_price'"):
            await client.get_index_price("btc_usd")
