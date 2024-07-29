from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

from serializers.prices import PriceRequest
from utils.price_helper import PriceHelper

router = APIRouter()


@router.websocket('/prices')
async def login(websocket: WebSocket):
    await websocket.accept()
    async with PriceHelper() as price_helper:
        while True:
            try:
                data = await websocket.receive_json()
                request_data = PriceRequest(**data)
                prices = await price_helper.get_prices(request_data)
                await websocket.send_json(prices)
            except WebSocketDisconnect:
                break
            except ValidationError as validation_error:
                errors = [{
                    'msg': error.get('msg'),
                    'input': error.get('input'),
                } for error in validation_error.errors()]
                await websocket.send_json({'error': errors})
            except Exception as e:
                await websocket.send_json({'error': str(e)})
                await websocket.close()
                break
