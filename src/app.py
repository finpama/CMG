from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import logging

from .Tol import TolController
from .Database import dbController
from .Database import dbModel

from pydantic import BaseModel
from typing import Any

from datetime import datetime as Date


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class defaltResponse(BaseModel):
    statusCode: str = "200"
    isError: bool = False
    errorMessage: str = "null"
    results: list[Any] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup:
    logger.info('running startup')
    
    logger.info('Creating database engine...')
    asyncio.create_task(dbController.createDb_engine())
    logger.info('Database engine created.')
    
    logger.info('Setting TOL auto refresher...')
    asyncio.create_task(TolController.auto_refresh())
    logger.info('TOL auto refresher set.')
    
    yield
    # shutdown:
    print('Running shutdown')
    
    

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_status():
    return {
        "last_refresh": TolController.lastRefresh,
    }



@app.get("/refresh")
async def refresh():
    await TolController.refresh()
    
    resultados = [{"new_refresh": TolController.lastRefresh}]
    return defaltResponse(results=resultados)



@app.post('/create-database')
async def createDB():
    
    asyncio.create_task(dbController.createDb_engine())
    
    return defaltResponse(results=[])


class InsertProcesso_request(BaseModel):
    namekey: str
    n_containers: int
    n_freetime: int | None = None
    data_eta: Date | None = None 
    numerario_fechado: bool = False
    excluido: bool = False
    

@app.post('/processo/novo')
async def insertProcesso(request_body: InsertProcesso_request):
    
    processo = dbModel.Processos(
        namekey = request_body.namekey,
        n_containers = request_body.n_containers,
        n_freetime = request_body.n_freetime,
        data_eta = request_body.data_eta,
        numerario_fechado = request_body.numerario_fechado,
        excluido = request_body.excluido,
    )
    
    task = asyncio.create_task(dbController.insert_processo(processo))
    await task
    
    tastResult = task.result()
    
    if tastResult == 0:
        response =  defaltResponse(statusCode='201',results=[{"created":processo}])
    else:
        response =  defaltResponse(statusCode='400',results=[{"failed_to_create":processo}], isError=True, errorMessage=tastResult.args[0])
    
    return response





if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
