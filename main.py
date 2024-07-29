import uvicorn
from fastapi import FastAPI

from endpoints import prices

app = FastAPI(title='KauriOneTT', version='0.0.1', description='TT')

app.include_router(prices.router, prefix='', tags=['prices'])


if __name__ == '__main__':
    uvicorn.run('main:app', port=8000, host='127.0.0.1', reload=True)
