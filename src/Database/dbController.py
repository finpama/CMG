
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import IntegrityError
import os

from . import dbModel


class DatabaseConfig:
    sqlite_file_path = "./"
    sqlite_file_name = "database.db"
    echo_SQL = True
    
    sqlite_url = f"sqlite:///{sqlite_file_name}"


ENGINE = create_engine(url=DatabaseConfig.sqlite_url, echo=DatabaseConfig.echo_SQL)


async def create_db():
    print('\n[dbController]: creating database')
    
    SQLModel.metadata.create_all(ENGINE)

async def insert_processo(processo: dbModel.Processos):
    
    try:
        with Session(ENGINE) as session:
            session.add(processo)
            session.commit()
            
            return 0
        
    except IntegrityError as e:
        return e
