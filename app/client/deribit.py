import aiohttp


class DeribitAPIError(Exception):
    """Ошибка API Deribit."""

    def __init__(self, message: str, code: int | None = None) -> None:
        self.code = code
        super().__init__(message)


class DeribitClient:
    """Клиент для публичного API Deribit.

    Позволяет получать index price для криптовалютных пар
    через публичный эндпоинт get_index_price (без аутентификации).
    """

    def __init__(self, base_url: str) -> None:
        self._base_url = base_url.rstrip("/")

    async def get_index_price(self, index_name: str) -> float:
        """Получить текущий index price для указанной валютной пары.

        Args:
            index_name: Название индекса, например 'btc_usd'.

        Returns:
            Текущий index price как float.

        Raises:
            DeribitAPIError: Если API вернул ошибку или некорректный ответ.
            aiohttp.ClientError: При сетевых проблемах.
        """
        url = f"{self._base_url}/public/get_index_price"

        async with aiohttp.ClientSession() as session:
            async with session.get(url, params={"index_name": index_name}) as response:
                response.raise_for_status()
                data = await response.json()

        if "error" in data:
            err = data["error"]
            raise DeribitAPIError(
                message=err.get("message", "Unknown API error"),
                code=err.get("code"),
            )

        result = data.get("result")
        if result is None:
            raise DeribitAPIError("API response missing 'result' field")

        index_price = result.get("index_price")
        if index_price is None:
            raise DeribitAPIError("API response missing 'index_price' in result")

        return float(index_price)
