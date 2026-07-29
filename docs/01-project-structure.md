# 01 — Структура проекта

## Решение

Проект организован по **слоёному принципу** (layered architecture):

```
app/              # core-приложение
├── api/          # слой API (эндпоинты FastAPI)
├── services/     # слой сервисов (бизнес-логика)
└── tasks/        # слой задач (Celery)
```

Каждый слой отвечает только за свою зону ответственности:

1. **API layer** (`app/api/`) — только обработка HTTP запросов, валидация, сериализация
2. **Service layer** (`app/services/`) — бизнес-логика, вызовы внешних API
3. **Task layer** (`app/tasks/`) — фоновые задачи, периодические операции
4. **Data layer** (`app/database.py`, `app/models.py`) — работа с БД

## Почему не monolithic?

- **Тестируемость**: каждый слой можно тестировать независимо
- **Заменяемость**: можно заменить HTTP клиент на gRPC, не трогая API слой
- **Читаемость**: новая функциональность сразу понятно куда добавлять

## Почему не flat?

С ростом проекта flat-структура (все файлы в одной папке) превращается в хаос. Разделение на слои с самого начала дешевле, чем рефакторинг потом.

## Структура папок

```
derbit_client/
├── app/                   # core-приложение
│   ├── __init__.py
│   ├── main.py            # FastAPI приложение (точка входа)
│   ├── config.py          # Конфигурация (pydantic-settings)
│   ├── database.py        # SQLAlchemy engine и сессии
│   ├── models.py          # ORM модели
│   ├── schemas.py         # Pydantic схемы
│   ├── api/               # HTTP слой
│   │   ├── __init__.py
│   │   └── prices.py      # Эндпоинты цен
│   ├── services/          # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── deribit_client.py   # Клиент Deribit API
│   │   └── price_service.py    # Сервис работы с ценами
│   └── tasks/             # Celery задачи
│       ├── __init__.py
│       └── price_tasks.py # Периодический сбор цен
├── tests/                 # Тесты (зеркалируют структуру app/)
│   ├── __init__.py
│   ├── test_imports.py
│   ├── test_api.py
│   ├── test_tasks.py
│   └── test_deribit_client.py
├── docs/                  # Документация как код
│   ├── 01-project-structure.md
│   ├── 02-config-and-database.md
│   ├── 03-deribit-client.md
│   ├── 04-celery-tasks.md
│   ├── 05-fastapi-endpoints.md
│   ├── 06-docker.md
│   └── testing-problems.md
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
├── .env.example
└── README.md
```

## Зависимости

| Пакет | Назначение |
|-------|-----------|
| fastapi | HTTP API |
| uvicorn | ASGI сервер |
| sqlalchemy + asyncpg | ORM + async драйвер PostgreSQL |
| aiohttp | Асинхронный HTTP клиент для Deribit |
| celery + redis | Фоновые задачи и периодический сбор |
| pydantic-settings | Конфигурация из переменных окружения |
| pytest + pytest-asyncio + pytest-mock + httpx | Тестирование |

## Команды

```bash
# Запуск всех сервисов
docker compose up --build

# Запуск только тестов
docker compose run --rm --no-deps app python -m pytest

# Запуск конкретного теста
docker compose run --rm --no-deps app python -m pytest tests/test_imports.py -v
```
