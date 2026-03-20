from fastapi import FastAPI
from contextlib import asynccontextmanager
import asyncio
from fastapi.middleware.cors import CORSMiddleware

from .Tol import TolController
from .Database import dbController

from pydantic import BaseModel
import json
from typing import Any



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



class createDB_request(BaseModel):
    name: str
    location: str
    dumpData: bool = False
    echoSQL: bool = False

@app.post('/create-database')
async def createDB(requestBody: createDB_request):
    
    name, path, echo = requestBody.name, requestBody.location, requestBody.echoSQL
    asyncio.create_task(dbController.create_db(name, path, echo))
    
    if requestBody.dumpData:
        print('DUMPING TUDO')
        # asyncio.create_task(TolController.dump_data())
    
    results = [{"request": requestBody}]
    return defaltResponse(results=results)