from sqlalchemy import BigInteger, Column, Float, Integer, String
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class PriceRecord(Base):
    __tablename__ = "price_records"

    id = Column(Integer, primary_key=True, autoincrement=True)
    ticker = Column(String(20), nullable=False, index=True)
    price = Column(Float, nullable=False)
    timestamp = Column(BigInteger, nullable=False, index=True)
