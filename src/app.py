from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio


from .Tol import TolController
from .Database import dbController
from .Database import dbModel

from pydantic import BaseModel
from typing import Any

from datetime import datetime as Date


class defaltResponse(BaseModel):
    statusCode: str = "200"
    isError: bool = False
    errorMessage: str = "null"
    results: list[Any] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup:
    print('\n[app]: running startup')
    asyncio.create_task(TolController.auto_refresh())
    
    
    yield
    # shutdown:
    print('\n[app]: running shutdown')
    
    

app = FastAPI(lifespan=lifespan)


@app.get("/")
def read_status():
    return {"last_refresh": TolController.lastRefresh}


class refresh_request(BaseModel):
    refreshLog: bool = False
    

@app.post("/refresh")
async def refresh(requestBody: refresh_request):
    await TolController.refresh(requestBody.refreshLog)
    
    results = [{"request": requestBody}, {"new_refresh": TolController.lastRefresh}]
    return defaltResponse(results=results)



@app.post('/create-database')
async def createDB():
    
    asyncio.create_task(dbController.create_db())
    
    
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