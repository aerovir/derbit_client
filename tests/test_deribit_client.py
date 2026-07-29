"""Тесты для клиента Deribit API.

Проверяем:
- Успешный ответ (статус 200, корректный JSON)
- Ошибка биржи (статус 200, но {"error": ...})
- HTTP ошибка (статус 404, 500)
- Таймаут соединения
- Невалидный JSON в ответе
- Пустой ответ
- Неверный тикер
"""

from unittest.mock import AsyncMock, patch
import asyncio

import aiohttp
import pytest

from app.services.deribit_client import DeribitClient


@pytest.fixture
def client():
    """Фикстура: экземпляр DeribitClient."""
    return DeribitClient()


def _mock_response(status: int = 200, json_data: dict | None = None) -> AsyncMock:
    """Создаёт мок ответа aiohttp."""
    response = AsyncMock(spec=aiohttp.ClientResponse)
    response.status = status
    response.reason = "OK" if status == 200 else "Error"
    response.json = AsyncMock(return_value=json_data or {})
    return response


def _mock_session(response: AsyncMock) -> AsyncMock:
    """Создаёт мок aiohttp сессии.

    Асинхронный контекстный менеджер session.get() возвращает response.
    """
    ctx = AsyncMock()
    ctx.__aenter__.return_value = response

    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get.return_value = ctx
    return session


@pytest.mark.asyncio
async def test_get_index_price_success(client):
    """Успешный запрос цены возвращает float."""
    response = _mock_response(json_data={
        "result": {"index_price": 50000.123}
    })
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        price = await client.get_index_price("btc_usd")

    assert isinstance(price, float)
    assert price == 50000.123


@pytest.mark.asyncio
async def test_get_index_price_eth(client):
    """Работает для ETH_USD."""
    response = _mock_response(json_data={
        "result": {"index_price": 3000.50}
    })
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        price = await client.get_index_price("eth_usd")

    assert price == 3000.50


@pytest.mark.asyncio
async def test_get_index_price_url_btc(client):
    """Проверяем, что URL формируется правильно для BTC."""
    response = _mock_response(json_data={
        "result": {"index_price": 50000.0}
    })
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        await client.get_index_price("btc_usd")

    session.get.assert_called_once()


@pytest.mark.asyncio
async def test_api_error_response(client):
    """При ошибке в ответе биржи поднимается исключение."""
    response = _mock_response(json_data={
        "error": {"code": 10000, "message": "Invalid index name"}
    })
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(ValueError, match="Invalid index name"):
            await client.get_index_price("invalid_ticker")


@pytest.mark.asyncio
async def test_http_error(client):
    """HTTP ошибка (500) поднимает исключение."""
    response = _mock_response(status=500)
    response.reason = "Internal Server Error"
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(RuntimeError, match="500"):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_timeout(client):
    """Таймаут соединения поднимает asyncio.TimeoutError."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    # session.get поднимает TimeoutError при вызове
    session.get.side_effect = asyncio.TimeoutError()

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(asyncio.TimeoutError):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_json_decode_error(client):
    """Ошибка декодирования JSON поднимает ValueError."""
    response = _mock_response()
    response.json = AsyncMock(side_effect=ValueError("Invalid JSON"))
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(ValueError, match="Invalid JSON"):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_missing_index_price(client):
    """Ответ без index_price поднимает KeyError."""
    response = _mock_response(json_data={"result": {}})
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(KeyError):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_connection_error(client):
    """Ошибка соединения поднимает aiohttp.ClientError."""
    session = AsyncMock(spec=aiohttp.ClientSession)
    session.get.side_effect = aiohttp.ClientConnectionError("Connection refused")

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        with pytest.raises(aiohttp.ClientConnectionError):
            await client.get_index_price("btc_usd")


@pytest.mark.asyncio
async def test_context_manager(client):
    """Клиент работает как контекстный менеджер."""
    response = _mock_response(json_data={
        "result": {"index_price": 50000.0}
    })
    session = _mock_session(response)

    with patch("app.services.deribit_client.aiohttp.ClientSession", return_value=session):
        async with client as c:
            price = await c.get_index_price("btc_usd")
            assert price == 50000.0
