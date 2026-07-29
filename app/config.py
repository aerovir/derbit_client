from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://deribit:deribit@localhost:5432/deribit"
    database_url_sync: str = "postgresql+psycopg2://deribit:deribit@localhost:5432/deribit"
    deribit_api_url: str = "https://test.deribit.com/api/v2"
    fetch_tickers: list[str] = ["btc_usd", "eth_usd"]

    model_config = {"env_prefix": "DERIBIT_"}


settings = Settings()
