import json
from more_itertools import chunked

import websockets
from loguru import logger

from .base_exchange import BaseExchange


KRAKEN_SOCKET = 'wss://ws.kraken.com/v2'


class Kraken(BaseExchange):

    async def __aenter__(self):
        self.websocket = await websockets.connect(KRAKEN_SOCKET)
        logger.info('Websocket connection for Kraken established')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info('Websocket connection for Kraken closed')
        await self.websocket.close()

    @staticmethod
    def _normalize_pair(pair: str):
        return pair.replace('_', '/')

    @staticmethod
    def _normalize_pair_to_output(pair: str):
        return pair.replace('/', '')

    async def get_prices(self, symbol):
        if not symbol:
            available_symbols_request = {
                "method": "subscribe",
                "params": {
                    "channel": "instrument"
                },
                "req_id": 79
            }
            await self.websocket.send(json.dumps(available_symbols_request))
            while True:
                response = await self.websocket.recv()
                logger.info(response)
                data = json.loads(response)
                if data.get('channel') == 'instrument':
                    available_symbols = [
                        self._normalize_pair(pair.get('symbol')) for pair in json.loads(response).get('data', {}).get('pairs', [])
                    ]
                    await self.unsubscribe_instrument()
                    break
        else:
            available_symbols = [self._normalize_pair(symbol)]

        chunked_available_symbols = chunked(available_symbols, 700)

        pair_response = {}

        for available_symbols in chunked_available_symbols:
            data = {
                "method": "subscribe",
                "params": {
                    "channel": "ticker",
                    "symbol": available_symbols
                }
            }
            await self.websocket.send(json.dumps(data))
            i = 0
            while i != len(available_symbols):
                logger.info(i)
                response = await self.websocket.recv()
                logger.info(response)
                data = json.loads(response)
                if data.get('channel') == 'ticker' and data.get('type') == 'snapshot':
                    for pair in data.get('data', []):
                        i += 1
                        logger.info(type(pair.get('last')))
                        pair_response[self._normalize_pair_to_output(pair.get('symbol'))] = pair.get('last')
                elif data.get('method') == 'subscribe' and data.get('success') is False:
                    i += 1
                    pair_response[self._normalize_pair_to_output(data.get('symbol'))] = 0

            await self.unsubscribe_symbols(available_symbols)

        return pair_response

    async def unsubscribe_instrument(self):
        unsubscribe = {
            "method": "unsubscribe",
            "params": {
                "channel": "instrument"
            },
            "req_id": 79
        }
        await self.websocket.send(json.dumps(unsubscribe))

    async def unsubscribe_symbols(self, available_symbols):
        unsubscribe = {
            "method": "unsubscribe",
            "params": {
                "channel": "ticker",
                "symbol": available_symbols
            }
        }
        await self.websocket.send(json.dumps(unsubscribe))
