from fastapi import FastAPI, Response, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
import uvicorn
from contextlib import asynccontextmanager
from sqlalchemy.exc import IntegrityError, NoResultFound
import asyncio
import logging

from .Tol import TolController
from .Database import dbController
from .Database.dbController import dbModel

from pydantic import BaseModel
from typing import Any

from datetime import datetime as Date
from dataclasses import dataclass


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class defaultResponse(BaseModel):
    statusCode: int = 200
    isError: bool = False
    errorMessage: str = "null"
    results: list[Any] = []


class DefaultResponse():
    statusCode: int 
    isError: bool 
    errorMessage: str
    results: list[Any]
    
    def __init__(self, statusCode=200, isError=False, errorMessage="null", results=[]) -> None:
        self.statusCode = statusCode
        self.isError = isError
        self.errorMessage = errorMessage
        self.results = results



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
    return defaultResponse(results=resultados)



class post_processo_request(BaseModel):
    namekey: str
    n_containers: int
    n_freetime: int | None = None
    data_eta: Date | None = None 
    numerario_fechado: bool = False
    excluido: bool = False
    

@app.post('/processo/novo')
async def post_processo(request_body: post_processo_request):
    
    processo = dbModel.Processos(
        namekey = request_body.namekey,
        n_containers = request_body.n_containers,
        n_freetime = request_body.n_freetime,
        data_eta = request_body.data_eta,
        numerario_fechado = request_body.numerario_fechado,
        excluido = request_body.excluido,
    )
    
    task = asyncio.create_task(dbController.create_processo(processo))
    await task
    
    tastResult = task.result()
    
    
    if not isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_201_CREATED, results=[{"created": request_body}])
    else:
        response = DefaultResponse(statusCode=status.HTTP_422_UNPROCESSABLE_CONTENT, results=[{"failed_to_create": request_body}], isError=True, errorMessage=tastResult.args[0])
    
    
    return JSONResponse(jsonable_encoder(response), response.statusCode)




class post_container_request(BaseModel):
    namekey: str
    tipo_container: str
    codigo_armador: str
    excluido: bool = False
    

@app.post('/container/novo')
async def post_container(request_body: post_container_request):
    
    containerDB = dbModel.Containers(
        namekey = request_body.namekey,
        tipo_container = request_body.tipo_container,
        codigo_armador = request_body.codigo_armador,
        excluido = request_body.excluido,
    )
    
    
    task = asyncio.create_task(dbController.create_container(containerDB))
    await task
    
    tastResult = task.result()
    
    
    if not isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_201_CREATED, results=[{"created": request_body}])
    else:
        response = DefaultResponse(statusCode=status.HTTP_422_UNPROCESSABLE_CONTENT, results=[{"failed_to_create": request_body}], isError=True, errorMessage=tastResult.args[0])
    
    
    return JSONResponse(jsonable_encoder(response), response.statusCode)




class post_carregamento_request(BaseModel):
    processo: str | None = None 
    container: str | None = None 
    terminal: str | None = None 
    transportadora: str | None = None
    status_agendamento: str | None = None 
    data_devolucao: Date | None = None 
    minuta_recebida: bool 
    demurrage: bool | None = None 
    data_inspecao: Date | None = None 
    cdk_tratativa: str | None = None 
    cobrancas_html: str | None = None 
    cobrancas_itens: str | None = None  # JSON Array (type notation: json[])
    data_solicitacao_isencao: Date | None = None 
    valor_devido: float | None = None 
    pagamento_realizado: bool
    arquivos_enviados: str 
    processo_finalizado: bool
    titulo_financeiro: str | None = None 
    excluido: bool = False

@app.post('/carregamento/novo')
async def post_carregamento(request_body: post_carregamento_request):
    
    carregamento = dbModel.Carregamentos(
        id = None,
        processo = request_body.processo, 
        container = request_body.container, 
        terminal = request_body.terminal, 
        transportadora = request_body.transportadora,
        status_agendamento = request_body.status_agendamento, 
        data_devolucao = request_body.data_devolucao, 
        minuta_recebida = request_body.minuta_recebida,
        demurrage = request_body.demurrage, 
        data_inspecao = request_body.data_inspecao, 
        cdk_tratativa = request_body.cdk_tratativa, 
        cobrancas_html = request_body.cobrancas_html, 
        cobrancas_itens = request_body.cobrancas_itens,  
        data_solicitacao_isencao = request_body.data_solicitacao_isencao, 
        valor_devido = request_body.valor_devido, 
        pagamento_realizado = request_body.pagamento_realizado,
        arquivos_enviados = request_body.arquivos_enviados,
        processo_finalizado = request_body.processo_finalizado,
        titulo_financeiro = request_body.titulo_financeiro, 
        excluido = request_body.excluido,
    )
    
    task = asyncio.create_task(dbController.create_carregamento(carregamento))
    await task
    
    tastResult = task.result()
    
    if not isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_201_CREATED, results=[{"created": tastResult}])
    else:
        response = DefaultResponse(statusCode=status.HTTP_400_BAD_REQUEST, results=[{"failed_to_create": carregamento}])
    
    
    return JSONResponse(jsonable_encoder(response), status_code=response.statusCode)



class patch_processo_request(BaseModel):
    n_containers: int | None = None
    n_freetime: int | None = None
    data_eta: Date | None = None 
    numerario_fechado: bool | None = None
    excluido: bool | None = None
    

@app.patch('/processo/{namekey}/editar')
async def patch_processo(namekey, request_body: patch_processo_request):
    
    task = asyncio.create_task(dbController.edit_processo(namekey, request_body))
    await task
    
    tastResult = task.result()
    

    if isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_400_BAD_REQUEST, results=[{"failed_to_edit":namekey}], isError=True, errorMessage=tastResult.args[0])    

    elif isinstance(tastResult, NoResultFound):
        response = DefaultResponse(statusCode=status.HTTP_404_NOT_FOUND, results=[{"failed_to_find": namekey}], isError=True, errorMessage=f'O {namekey} não foi encontrado.')

    else:
        response = DefaultResponse(statusCode=status.HTTP_200_OK, results=[{"edited_successfuly": tastResult}])
    
    
    return JSONResponse(jsonable_encoder(response), status_code=response.statusCode)



class patch_container_request(BaseModel):
    tipo_container: str | None = None
    codigo_armador: str | None = None
    excluido: bool | None = None
    

@app.patch('/container/{namekey}/editar')
async def patch_container(namekey, request_body: patch_container_request):
    
    task = asyncio.create_task(dbController.edit_container(namekey, request_body))
    await task
    
    tastResult = task.result()
    
    if isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_400_BAD_REQUEST, results=[{"failed_to_edit":namekey}], isError=True, errorMessage=tastResult.args[0])    

    elif isinstance(tastResult, NoResultFound):
        response = DefaultResponse(statusCode=status.HTTP_404_NOT_FOUND, results=[{"failed_to_find": namekey}], isError=True, errorMessage=f'O {namekey} não foi encontrado.')

    else:
        response = DefaultResponse(statusCode=status.HTTP_200_OK, results=[{"edited_successfuly": tastResult}])
    
    
    return JSONResponse(jsonable_encoder(response), status_code=response.statusCode)



class patch_carregamento_request(BaseModel):
    tipo_container: str | None = None
    codigo_armador: str | None = None
    excluido: bool | None = None
    

@app.patch('/carregamento/{id}/editar')
async def patch_carregamento(id, request_body: patch_carregamento_request):
    
    task = asyncio.create_task(dbController.edit_carregamento(id, request_body))
    await task
    
    tastResult = task.result()
    
    if isinstance(tastResult, IntegrityError):
        response = DefaultResponse(statusCode=status.HTTP_400_BAD_REQUEST, results=[{"failed_to_edit":id}], isError=True, errorMessage=tastResult.args[0])    

    elif isinstance(tastResult, NoResultFound):
        response = DefaultResponse(statusCode=status.HTTP_404_NOT_FOUND, results=[{"failed_to_find": id}], isError=True, errorMessage=f'O carregamento id:{id} não foi encontrado.')

    else:
        response = DefaultResponse(statusCode=status.HTTP_200_OK, results=[{"edited_successfuly": tastResult}])
    
    
    return JSONResponse(jsonable_encoder(response), status_code=response.statusCode)




if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
