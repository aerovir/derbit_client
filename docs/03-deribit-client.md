# 03 — Клиент Deribit

## Решение

Класс `DeribitClient` в `app/services/deribit_client.py` — асинхронный HTTP клиент для Deribit API на **aiohttp**.

### Поддерживаемый метод API

```
GET /public/get_index_price?index_name=btc_usd
```

Ответ Deribit:
```json
{
    "result": {
        "index_price": 50000.123
    }
}
```

### Использование

```python
# Через контекстный менеджер
async with DeribitClient() as client:
    price = await client.get_index_price("btc_usd")

# Без контекстного менеджера
client = DeribitClient()
price = await client.get_index_price("btc_usd")
await client.close()
```

### Обработка ошибок

| Ситуация | Исключение |
|----------|-----------|
| HTTP статус != 200 | `RuntimeError` |
| `{"error": {...}}` в ответе | `ValueError` |
| Таймаут | `asyncio.TimeoutError` |
| Ошибка соединения | `aiohttp.ClientError` |
| Отсутствует `index_price` | `KeyError` |

### Почему aiohttp?

- **Неблокирующие** запросы (в отличие от `requests`)
- **Native async/await** — нет пула потоков
- Стандарт для асинхронных HTTP клиентов в Python

### Почему не Deribit SDK?

- Нет официального Python SDK от Deribit
- API простой (один эндпоинт) — клиент на 50 строк кода
- Полный контроль над ошибками и таймаутами

## Тестирование

Моки aiohttp через `AsyncMock`:

```python
# Схема мока:
# aiohttp.ClientSession.get() → async ctx manager
#   ctx.__aenter__ → response (status, json)
#   ctx.__aexit__ → None
```

Тесты покрывают: успех, ошибка биржи, HTTP ошибка, таймаут,
невалидный JSON, отсутствие поля `index_price`, ошибка соединения.
