# Deribit Price Client

Клиент для получения текущих цен криптовалют с биржи Deribit и сохранения их в PostgreSQL. Предоставляет FastAPI для доступа к сохранённым данным.

## Требования

- Docker и Docker Compose

## Быстрый старт

```bash
# Склонировать репозиторий
git clone <repo-url> && cd derbit_client

# Запустить приложение
docker compose up --build
```

Через минуту после запуска начнут появляться данные.

## API Endpoints

Все методы — GET, у каждого обязательный query-параметр `ticker`.

### Получить все цены для валюты

```
GET /api/v1/prices?ticker=btc_usd
```

Опциональные параметры:
- `date_from` — UNIX timestamp, начало периода
- `date_to` — UNIX timestamp, конец периода

Пример с фильтром:
```
GET /api/v1/prices?ticker=btc_usd&date_from=1700000000&date_to=1799999999
```

### Получить последнюю цену

```
GET /api/v1/prices/last?ticker=btc_usd
```

### Примеры ответов

```json
// GET /api/v1/prices?ticker=btc_usd
[
  {
    "id": 1,
    "ticker": "btc_usd",
    "price": 64488.96,
    "timestamp": 1700000000
  }
]

// GET /api/v1/prices/last?ticker=btc_usd
{
  "ticker": "btc_usd",
  "price": 64488.96,
  "timestamp": 1700000000
}
```

## Разворачивание

Приложение состоит из двух Docker-контейнеров:

| Контейнер | Назначение |
|-----------|-----------|
| `app` | FastAPI + Celery worker + Celery beat |
| `db` | PostgreSQL 16 |

### Переменные окружения

Все переменные имеют префикс `DERIBIT_`:

| Переменная | Значение по умолчанию | Описание |
|-----------|----------------------|----------|
| `DERIBIT_DATABASE_URL` | `postgresql+asyncpg://deribit:deribit@db:5432/deribit` | Async connection to PostgreSQL |
| `DERIBIT_DATABASE_URL_SYNC` | `postgresql+psycopg2://deribit:deribit@db:5432/deribit` | Sync connection for Celery |
| `DERIBIT_DERIBIT_API_URL` | `https://test.deribit.com/api/v2` | Deribit API base URL |
| `DERIBIT_FETCH_TICKERS` | `["btc_usd","eth_usd"]` | Список тикеров для отслеживания |

### Запуск

```bash
docker compose up --build
```

Приложение будет доступно на `http://localhost:8000`.

### Тестирование

```bash
docker compose run --rm app pytest -v
```

## Project Structure

```
derbit_client/
├── app/
│   ├── api/
│   │   └── prices.py          # FastAPI endpoints (3 routes)
│   ├── client/
│   │   └── deribit.py         # Deribit API client (aiohttp)
│   ├── tasks/
│   │   ├── celery_app.py      # Celery app (SQLAlchemy transport)
│   │   └── fetch_prices.py    # Периодическая задача
│   ├── config.py              # Pydantic Settings
│   ├── database.py            # Async SQLAlchemy engine
│   ├── main.py                # FastAPI app
│   ├── models.py              # PriceRecord ORM модель
│   └── schemas.py             # Pydantic схемы
├── tests/
│   ├── conftest.py            # Shared fixtures
│   ├── test_api.py            # API endpoint tests (9)
│   ├── test_client.py         # DeribitClient tests (7)
│   ├── test_database.py       # Database tests (8)
│   └── test_tasks.py          # Celery task tests (3)
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
└── requirements.txt
```

## Design Decisions

### 1. Два контейнера вместо трёх+ (app + db)

Celery использует **SQLAlchemy transport** (`sqla+postgresql://`) вместо Redis или RabbitMQ. Это позволяет:
- Не поднимать отдельный брокер сообщений
- Уложиться в 2 контейнера (приложение + БД)
- Упростить разворачивание

В контейнере `app` через entrypoint-скрипт запускаются три процесса:
- `celery worker` — обработчик задач
- `celery beat` — планировщик (каждые 60 секунд)
- `uvicorn` — FastAPI сервер

### 2. Async везде, кроме Celery

FastAPI и DeribitClient используют asyncio (aiohttp + asyncpg + async SQLAlchemy). Celery задача использует отдельный sync-движок (psycopg2) и thread-based event loop bridge для вызова async-клиента. Это позволяет сохранить единый async-код для бизнес-логики при sync-природе Celery.

### 3. TDD-подход

Каждый компонент написан по методологии TDD: сначала тесты, потом реализация. Для каждого компонента создавалась отдельная ветка:
- `feature/deribit-client`
- `feature/database-model`
- `feature/celery-tasks`
- `feature/api-endpoints`

### 4. Публичный API Deribit

Используется публичный эндпоинт `public/get_index_price`, не требующий аутентификации. Для production рекомендуется переключиться на `https://www.deribit.com/api/v2`.

### 5. Индексы БД

Поля `ticker` и `timestamp` индексированы для быстрых поисков по валютной паре и временным диапазонам — основным сценариям запросов API.

### 6. Graceful error handling

- Celery задача обрабатывает ошибки API для каждого тикера независимо (один тикер может упасть, другой — успешно сохраниться)
- При трёх последовательных ошибках задача перестаёт ретраиться
- FastAPI возвращает 404 для последней цены, если данных нет
- DeribitClient проверяет структуру ответа API и поднимает понятные исключения при невалидных данных
