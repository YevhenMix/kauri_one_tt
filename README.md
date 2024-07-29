## App Startup

In the root directory of the project run ```make build_service``` and then 
```make start_service``` which will start the container with the application.

## App Description

In the application there is one endpoint that opens a websocket connection ```ws://127.0.0.1:8000/prices```

This endpoint accepts an object that consists of two fields 
```json
{
  "exchange": "binance",
  "pair": "BTC_USDT"
}
```
The **exchange** field can be either **binance** or **kraken** or **null**

The **pair** field can be either a **string** with uppercase names of pairs separated by underscores or **null**

## Response Example

A successful response has the following structure: it is a list of dicts with the requested data

```json
[
  {
    "symbol": "BTCUSDT",
    "price_on_exchanges": [
      {
        "exchange": "binance",
        "price": 67000.01
      },
      {
        "exchange": "kraken",
        "price": 67001.01
      }
    ]
  }
]
```

If a specific exchange is not requested and there is no pair on some exchange that exist on another, 
the price value will be 0 for that exchange. If a specific exchange is passed, the response will contain no objects with prices for other exchanges.
