from enum import Enum
from typing import Optional
from typing_extensions import Self

from pydantic import BaseModel, field_validator


class Exchange(str, Enum):
    BINANCE = 'binance'
    KRAKEN = 'kraken'


class PriceRequest(BaseModel):
    pair: Optional[str]
    exchange: Optional[Exchange]

    @field_validator('pair')
    def check_passwords_match(cls, value, info) -> Self:
        if value and '_' not in value:
            raise ValueError('Add separator (_ symbol) to pair, to correctly split them and pass to exchanges')
        return value
