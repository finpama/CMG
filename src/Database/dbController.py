
from sqlmodel import SQLModel, create_engine, Session, select, func
from sqlalchemy.exc import IntegrityError
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
    logger.info(f'\n[dbController]: creating or/and loading the database in "{DatabaseConfig.sqlite_file_name}" with the engine.')
    
    SQLModel.metadata.create_all(ENGINE)

async def insert_processo(processo: dbModel.Processos):
    
    try:
        with Session(ENGINE) as session:
            session.add(processo)
            session.commit()
            
            return 0
        
    except IntegrityError as e:
        return e

async def insert_dados_tol(dado_tol: dbModel.Dados_tol):
    try:
        with Session(ENGINE) as session:
            session.add(dado_tol)
            session.commit()
            
            return 0
            
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
