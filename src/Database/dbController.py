
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError
from dataclasses import dataclass
import os

from . import dbModel


@dataclass
class DatabaseInfo:
    sqlite_file_name = "database.db"
    sqlite_file_path = "./"
    sqlite_url = f"sqlite:///{sqlite_file_name}"
    
    isClean = os.path.isfile(sqlite_file_path + sqlite_file_name)
    databaseEcho = True


async def create_db():
    print('\n[dbController]: creating database')
    
    dbInfo = DatabaseInfo()
    engine = create_engine(dbInfo.sqlite_url, echo=dbInfo.databaseEcho)
    
    SQLModel.metadata.create_all(engine)
