from fastapi import FastAPI
import uvicorn
from contextlib import asynccontextmanager
import asyncio
import logging

from .Tol import TolController
from .Database import dbController
from .Database.dbController import dbModel

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
    
    task = asyncio.create_task(dbController.insert_processo(processo))
    await task
    
    tastResult = task.result()
    
    if tastResult == 0:
        response =  defaltResponse(statusCode='201',results=[])
    else:
        response =  defaltResponse(statusCode='400',results=[{"failed_to_create":processo}], isError=True, errorMessage=tastResult.args[0])
    
    return response


class post_container_request(BaseModel):
    namekey: str
    tipo_container: str
    codigo_armador: str
    excluido: bool = False
    


@app.post('/container/novo')
async def post_container(request_body: post_container_request):
    
    container = dbModel.Containers(
        namekey = request_body.namekey,
        tipo_container = request_body.tipo_container,
        codigo_armador = request_body.codigo_armador,
        excluido = request_body.excluido,
    )
    
    task = asyncio.create_task(dbController.insert_container(container))
    await task
    
    tastResult = task.result()
    
    if tastResult == 0:
        response =  defaltResponse(statusCode='201',results=[])
    else:
        response =  defaltResponse(statusCode='400',results=[{"failed_to_create":container}], isError=True, errorMessage=tastResult.args[0])
    
    return response


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
    
    task = asyncio.create_task(dbController.insert_carregamento(carregamento))
    await task
    
    tastResult = task.result()
    
    if tastResult == 0:
        response =  defaltResponse(statusCode='201',results=[])
    else:
        response =  defaltResponse(statusCode='400',results=[{"failed_to_create":carregamento}], isError=True, errorMessage=tastResult.args[0])
    
    return response





if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
