# Проблемы тестирования

## 1. pydantic-settings: JSON-парсинг сложных типов

**Проблема:** pydantic-settings 2.5.2 вызывает `json.loads()` для env-переменных с комплексными типами (например, `list[str]`). Если значение не является валидным JSON (например, `TICKERS=btc_usd,eth_usd`), падает с `SettingsError`.

Трассировка:
```
EnvSettingsSource.decode_complex_value() → json.loads(value) → JSONDecodeError
```

**Решение:** Хранить TICKERS как `str` и добавить свойство `ticker_list`, которое парсит строку через запятую.

```python
# Вместо:
TICKERS: list[str] = ["btc_usd", "eth_usd"]

# Используем:
TICKERS: str = "btc_usd,eth_usd"

@property
def ticker_list(self) -> list[str]:
    return [t.strip() for t in self.TICKERS.split(",") if t.strip()]
```

**Почему не `field_validator` / `BeforeValidator`?** Потому что `decode_complex_value` вызывается до валидации, на этапе парсинга источников (EnvSettingsSource).

## 2. Тестирование async генераторов

**Проблема:** `get_session()` — async генератор. Для его тестирования нужно либо вызвать `async for` один раз и выйти, либо использовать `anext()`.

**Решение:** Используем `async for session in get_session(): ... break`.

## 3. Docker и файлы тестов

**Проблема:** Файлы, добавленные после сборки образа, не видны в контейнере. Каждое изменение требует пересборки.

**Решение:** Добавлен `docker-compose.dev.yml` с volume mount `.` в `/app`. Теперь все изменения отражаются мгновенно.

```bash
# Запуск с монтированием кода (для разработки)
docker compose -f docker-compose.yml -f docker-compose.dev.yml run --rm --no-deps app pytest
```
