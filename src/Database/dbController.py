
from sqlmodel import SQLModel, create_engine, Session, select, func
from sqlalchemy.exc import IntegrityError, NoResultFound
from typing import Literal
import logging

from ..utils.config_reader import read_configFile
from ..Database import dbModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

config = read_configFile('databaseConfig')

class DatabaseConfig:
    sqlite_file_name = config['sqlite_file_name']
    echo_SQL = config['echo_SQL']
    
    sqlite_url = f"sqlite:///{sqlite_file_name}"


ENGINE = create_engine(url=DatabaseConfig.sqlite_url, echo=DatabaseConfig.echo_SQL)


async def createDb_engine():
    logger.info(f'Creating or/and loading the database in "{DatabaseConfig.sqlite_file_name}" with the engine.')
    
    SQLModel.metadata.create_all(ENGINE)



async def create_processo(processo: dbModel.Processos):
    try:
        with Session(ENGINE) as session:
            session.add(processo)
            session.commit()
            
            return processo
        
    except IntegrityError as e:
        return e

async def edit_processo(namekey, novosDados):
    try:
        with Session(ENGINE) as session:
            query = select(dbModel.Processos).where(dbModel.Processos.namekey == namekey)
            results = session.exec(query)
            processo = results.one()
            
            if novosDados.n_containers != None:
                processo.n_containers = novosDados.n_containers
            
            if novosDados.n_freetime != None:
                processo.n_freetime = novosDados.n_freetime
            
            if novosDados.data_eta != None:
                processo.data_eta = novosDados.data_eta
            
            if novosDados.numerario_fechado != None:
                processo.numerario_fechado = novosDados.numerario_fechado
            
            if novosDados.excluido != None:
                processo.excluido = novosDados.excluido
            
            session.add(processo)
            session.commit()
            session.refresh(processo)
            
            return processo
        
    except (IntegrityError, NoResultFound) as e:
        return e


async def create_container(container: dbModel.Containers):
    try:
        with Session(ENGINE) as session:
            session.add(container)
            session.commit()
            
            return container
        
    except IntegrityError as e:
        return e

async def edit_container(namekey, novosDados):
    try:
        with Session(ENGINE) as session:
            query = select(dbModel.Containers).where(dbModel.Containers.namekey == namekey)
            results = session.exec(query)
            container = results.one()
            
            if novosDados.tipo_container != None:
                container.tipo_container = novosDados.tipo_container
                
            if novosDados.codigo_armador != None:
                container.codigo_armador = novosDados.codigo_armador
                
            if novosDados.excluido != None:
                container.excluido = novosDados.excluido
            
            session.add(container)
            session.commit()
            session.refresh(container)
            
            return container
        
    except (IntegrityError, NoResultFound)  as e:
        return e



async def create_carregamento(carregamento: dbModel.Carregamentos):
    try:
        with Session(ENGINE) as session:
            session.add(carregamento)
            session.commit()
            
            return carregamento
        
    except IntegrityError as e:
        return e

async def edit_carregamento(id, novosDados):
    try:
        with Session(ENGINE) as session:
            query = select(dbModel.Carregamentos).where(dbModel.Carregamentos.id == id)
            results = session.exec(query)
            carregamento = results.one()
            
            if (novosDados.processo != None) : carregamento.processo = novosDados.processo
            if (novosDados.container != None) : carregamento.container = novosDados.container
            if (novosDados.data_presenca_carga != None) : carregamento.data_presenca_carga = novosDados.data_presenca_carga
            if (novosDados.terminal != None) : carregamento.terminal = novosDados.terminal
            if (novosDados.transportadora != None) : carregamento.transportadora = novosDados.transportadora
            if (novosDados.status_agendamento != None) : carregamento.status_agendamento = novosDados.status_agendamento
            if (novosDados.data_devolucao != None) : carregamento.data_devolucao = novosDados.data_devolucao
            if (novosDados.minuta_recebida != None) : carregamento.minuta_recebida = novosDados.minuta_recebida
            if (novosDados.demurrage != None) : carregamento.demurrage = novosDados.demurrage
            if (novosDados.data_inspecao != None) : carregamento.data_inspecao = novosDados.data_inspecao
            if (novosDados.cdk_tratativa != None) : carregamento.cdk_tratativa = novosDados.cdk_tratativa
            if (novosDados.cobrancas_html != None) : carregamento.cobrancas_html = novosDados.cobrancas_html
            if (novosDados.cobrancas_itens != None) : carregamento.cobrancas_itens = novosDados.cobrancas_itens
            if (novosDados.data_solicitacao_isencao != None) : carregamento.data_solicitacao_isencao = novosDados.data_solicitacao_isencao
            if (novosDados.valor_devido != None) : carregamento.valor_devido = novosDados.valor_devido
            if (novosDados.titulo_financeiro != None) : carregamento.titulo_financeiro = novosDados.titulo_financeiro
            if (novosDados.pagamento_realizado != None) : carregamento.pagamento_realizado = novosDados.pagamento_realizado
            if (novosDados.arquivos_enviados != None) : carregamento.arquivos_enviados = novosDados.arquivos_enviados
            if (novosDados.processo_finalizado != None) : carregamento.processo_finalizado = novosDados.processo_finalizado
            if (novosDados.excluido != None) : carregamento.excluido = novosDados.excluido
            
            session.add(carregamento)
            session.commit()
            session.refresh(carregamento)
            
            return carregamento
        
    except (IntegrityError, NoResultFound) as e:
        return e


async def create_dados_tol(dado_tol: dbModel.Dados_tol):
    try:
        with Session(ENGINE) as session:
            session.add(dado_tol)
            session.commit()
            
            return
            
    except IntegrityError as e:
        return e

async def selectById_dados_tol(id: int | Literal['latest'] = 'latest'):
    try:
        with Session(ENGINE) as session:
            
            if id != 'latest':
                statement = select(dbModel.Dados_tol).where(dbModel.Dados_tol.id == id)
            else:
                statement = select(dbModel.Dados_tol.id, func.max(dbModel.Dados_tol.data_refresh), dbModel.Dados_tol.dados_agendamento, dbModel.Dados_tol.dados_processos)
            
            result = session.exec(statement).one()
            
            return result
            
    except IntegrityError as e:
        return e
