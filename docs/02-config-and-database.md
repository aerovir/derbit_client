# 02 — Конфигурация и База данных

## Конфигурация (`app/config.py`)

### Решение
Используем **pydantic-settings** для управления конфигурацией.

Параметры загружаются из:
1. Переменных окружения (приоритет)
2. `.env` файла (если существует)
3. Значений по умолчанию (низший приоритет)

### Параметры

| Параметр | Тип | По умолчанию | Описание |
|----------|-----|-------------|----------|
| `DB_URL` | str | `postgresql+asyncpg://...` | URL подключения к PostgreSQL |
| `REDIS_URL` | str | `redis://localhost:6379/0` | URL Redis (брокер Celery) |
| `DERIBIT_API_URL` | str | `https://www.deribit.com/api/v2` | Базовый URL Deribit API |
| `TICKERS` | str | `btc_usd,eth_usd` | Тикеры через запятую |
| `FETCH_INTERVAL_MINUTES` | int | `1` | Интервал сбора цен |

### Почему pydantic-settings?
- Автоматическая валидация типов
- Загрузка из env-файлов из коробки
- Интеграция с Pydantic (одна экосистема с FastAPI)

### Почему TICKERS — строка, а не список?
pydantic-settings 2.5 пытается JSON-парсить поля с типом `list[str]` из env-переменных. Чтобы сохранить UX (`TICKERS=btc_usd,eth_usd`), храним как строку и предоставляем свойство `ticker_list` для доступа как к списку.

## База данных (`app/database.py`)

### Решение
Используем **SQLAlchemy 2.0 asyncio** для асинхронной работы с PostgreSQL.

Компоненты:
- `engine` — асинхронный engine (asyncpg драйвер)
- `async_session_factory` — фабрика сессий
- `init_db()` — создание таблиц при старте
- `get_session()` — FastAPI dependency для получения сессии

### Почему asyncio?
- FastAPI асинхронный — нет смысла блокировать event loop
- asyncpg — самый быстрый драйвер PostgreSQL для Python
- SQLAlchemy 2.0 asyncio стабилен и хорошо документирован

## Модель (`app/models.py`)

```python
class PriceRecord(Base):
    __tablename__ = "prices"
    id: int (PK, автоинкремент)
    ticker: str (индексирован)
    price: float
    timestamp: int (UNIX timestamp, индексирован)
```

### Индексы
- `ticker` — для фильтрации по валюте
- `timestamp` — для фильтрации по дате

Составной индекс (ticker, timestamp) будет добавлен позже при профилировании — сейчас это преждевременная оптимизация.
