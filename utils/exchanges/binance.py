import json

import websockets
from loguru import logger

from .base_exchange import BaseExchange


BINANCE_SOCKET = 'wss://ws-api.binance.com:443/ws-api/v3'


class Binance(BaseExchange):

    async def __aenter__(self):
        self.websocket = await websockets.connect(BINANCE_SOCKET)
        logger.info('Websocket connection for Binance established')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info('Websocket connection for Binance closed')
        await self.websocket.close()

    @staticmethod
    def _normalize_pair(pair: str):
        return pair.replace('_', '')

    async def get_prices(self, symbol):
        data = {
            "id": "043a7cf2-bde3-4888-9604-c8ac41fcba4d",
            "method": "ticker.price",
        }
        if symbol:
            data["params"] = {"symbol": self._normalize_pair(symbol)}
        await self.websocket.send(json.dumps(data))
        message = await self.websocket.recv()
        response = json.loads(message)
        if response.get('status', 400) == 200:
            if isinstance(response['result'], list):
                response = {pair_price.get('symbol'): float(pair_price.get('price')) for pair_price in response['result']}
            else:
                pair_price = response['result']
                response = {pair_price.get('symbol'): float(pair_price.get('price'))}
        else:
            response = {symbol: 0}
        return response
