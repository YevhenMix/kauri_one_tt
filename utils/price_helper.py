from typing import Dict

from serializers.prices import PriceRequest, Exchange
from .exchanges.binance import Binance
from .exchanges.kraken import Kraken

SUPPORTED_EXCHANGES = {
    Exchange.BINANCE.value: Binance,
    Exchange.KRAKEN.value: Kraken,
}


class PriceHelper:
    def __init__(self):
        self.exchanges = {}

    async def __aenter__(self):
        for exchange_name, exchange in SUPPORTED_EXCHANGES.items():
            self.exchanges[exchange_name] = await exchange().__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        for exchange in self.exchanges.values():
            await exchange.__aexit__(exc_type, exc_val, exc_tb)

    async def get_prices(self, price_filter: PriceRequest):
        if price_filter.exchange:
            price = await self.exchanges[price_filter.exchange].get_prices(price_filter.pair)
            price = self._prepare_response(price, False, price_filter.exchange)
        else:
            price = {}
            for exchange_name, exchange in self.exchanges.items():
                price[exchange_name] = await exchange.get_prices(price_filter.pair)
            price = self._prepare_response(price, True)

        return price

    def _prepare_response(self, price: Dict, combine: bool, exchange: str = None):
        if not combine:
            result = [
                {'symbol': symbol, 'price_on_exchanges': [{
                    'exchange': exchange, 'price': price
                }]} for symbol, price in price.items()
            ]
        else:
            result = []
            all_symbols = set()

            for exchange in price.values():
                all_symbols.update(exchange.keys())

            for symbol in all_symbols:
                symbol_data = {
                    'symbol': symbol,
                    'price_on_exchanges': []
                }

                for exchange_name, exchange_data in price.items():
                    if symbol in exchange_data:
                        symbol_data['price_on_exchanges'].append({
                            'exchange': exchange_name,
                            'price': exchange_data[symbol]
                        })
                    else:
                        symbol_data['price_on_exchanges'].append({
                            'exchange': exchange_name,
                            'price': 0
                        })

                result.append(symbol_data)

        return result

