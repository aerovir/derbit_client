# Deribit Price Client

Клиент для криптобиржи Deribit, который периодически собирает индексные цены BTC_USD и ETH_USD и предоставляет API для доступа к данным.

## Требования

- Docker и Docker Compose

## Быстрый старт

```bash
docker compose up --build
```

## Структура проекта

Проект организован по слоёному принципу:

- `app/` — core-приложение (FastAPI + Celery)
- `tests/` — тесты
- `docs/` — документация

Подробнее — в [docs/](docs/).
