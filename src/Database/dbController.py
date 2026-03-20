
from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy.exc import OperationalError
from dataclasses import dataclass
import os

from . import dbModel


class DatabaseInfo:
    def __init__(self, filename="database.db", path="./", echoing=True):
        self.sqlite_file_name = filename
        self.sqlite_file_path = path
        self.databaseEcho = echoing
    
        self.sqlite_url = f"sqlite:///{self.sqlite_file_name}"
        self.isClean = os.path.isfile(self.sqlite_file_path + self.sqlite_file_name)


async def create_db(name:str, path:str, echo:bool):
    print('\n[dbController]: creating database')
    
    dbInfo = DatabaseInfo(name, path, echo)
    engine = create_engine(dbInfo.sqlite_url, echo=dbInfo.databaseEcho)
    
    SQLModel.metadata.create_all(engine)
