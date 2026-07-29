from pydantic import BaseModel


class PriceResponse(BaseModel):
    id: int
    ticker: str
    price: float
    timestamp: int

    model_config = {"from_attributes": True}


class PriceLastResponse(BaseModel):
    ticker: str
    price: float
    timestamp: int
