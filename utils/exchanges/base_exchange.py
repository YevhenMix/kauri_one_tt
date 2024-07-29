from abc import ABCMeta, abstractmethod
from typing import Optional


class BaseExchange(metaclass=ABCMeta):

    @abstractmethod
    async def get_prices(self, symbol: Optional[str]):
        pass
