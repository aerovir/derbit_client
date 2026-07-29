"""Клиент для взаимодействия с API криптобиржи Deribit.

Использует aiohttp для асинхронных HTTP запросов.
Поддерживает получение индексных цен (get_index_price).

Документация Deribit API:
https://docs.deribit.com/#public-get_index_price
"""

from typing import Optional

import aiohttp

from app.config import settings


class DeribitClient:
    """Асинхронный клиент для Deribit API.

    Пример использования:
        async with DeribitClient() as client:
            price = await client.get_index_price("btc_usd")
    """

    BASE_URL: str = settings.DERIBIT_API_URL
    TIMEOUT: int = 10  # секунд

    def __init__(self) -> None:
        self._session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "DeribitClient":
        """Вход в контекстный менеджер."""
        return self

    async def __aexit__(self, *args: object) -> None:
        """Выход из контекстного менеджера — закрытие сессии."""
        await self.close()

    async def _get_session(self) -> aiohttp.ClientSession:
        """Возвращает или создаёт aiohttp сессию."""
        if self._session is None or self._session.closed:
            timeout = aiohttp.ClientTimeout(total=self.TIMEOUT)
            self._session = aiohttp.ClientSession(timeout=timeout)
        return self._session

    async def close(self) -> None:
        """Явное закрытие сессии."""
        if self._session is not None and not self._session.closed:
            await self._session.close()

    async def get_index_price(self, ticker: str) -> float:
        """Получение индексной цены валюты.

        Args:
            ticker: Тикер валюты (например, "btc_usd", "eth_usd").

        Returns:
            Текущая индексная цена как float.

        Raises:
            ValueError: Если биржа вернула ошибку или неверный тикер.
            RuntimeError: При HTTP ошибке (статус != 200).
            aiohttp.ClientError: При проблемах соединения.
            KeyError: Если в ответе отсутствует index_price.
        """
        session = await self._get_session()
        url = f"{self.BASE_URL}/public/get_index_price"
        params = {"index_name": ticker}

        async with session.get(url, params=params) as response:
            if response.status != 200:
                raise RuntimeError(
                    f"Deribit API вернул HTTP {response.status}: {response.reason}"
                )

            data = await response.json()

            if "error" in data:
                error_info = data["error"]
                error_message = error_info.get(
                    "message", "Unknown error"
                )
                raise ValueError(f"Deribit API error: {error_message}")

            return float(data["result"]["index_price"])
