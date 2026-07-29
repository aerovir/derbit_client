"""SQLAlchemy модели данных.

Определяет структуру таблиц в базе данных.
"""

from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class PriceRecord(Base):
    """Модель для хранения цен валют с биржи Deribit.

    Attributes:
        id: Уникальный идентификатор записи (автоинкремент)
        ticker: Тикер валюты (например, btc_usd, eth_usd)
        price: Текущая индексная цена
        timestamp: UNIX timestamp получения цены
    """

    __tablename__ = "prices"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(20), index=True, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    timestamp: Mapped[int] = mapped_column(Integer, index=True, nullable=False)

    def __repr__(self) -> str:
        return (
            f"PriceRecord(id={self.id}, ticker='{self.ticker}', "
            f"price={self.price}, timestamp={self.timestamp})"
        )
