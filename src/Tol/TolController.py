import asyncio
import requests as req
import json
from dataclasses import dataclass

from datetime import datetime

from ..Database import dbController

lastRefresh = datetime.now()
refreshDelay = 60 * 5 #Em segundos

@dataclass
class Tol_data:
    appointment: object
    process: object


def requestToken() -> str:
    with open('./password.json') as pw:
        jsonPW = json.loads(pw.read())

    response = req.post('https://purcell.terminalonline.com.br/authenticate', json=jsonPW)

    data = json.loads(response.content)
    data_results = data.get('results')
    TOKEN = data_results.get('token')
    
    return TOKEN

def appointmentRequest(session:req.Session):
    return session.get('https://purcell.terminalonline.com.br/appointment/list/importer')

def processRequest(session:req.Session):
    return session.get('https://purcell.terminalonline.com.br/Importer/thirdparty/gapi')


TOKEN = requestToken()

Session = req.session()
Session.headers.update({"Authorization": f"Bearer {TOKEN}"})


async def refresh(iWithLog: bool):
    global lastRefresh
    lastRefresh = datetime.now()
    
    TOL_appointmentData = appointmentRequest(Session).json()
    TOL_processData = processRequest(Session).json()
    
    appointmentData = TOL_appointmentData['results']
    processData = TOL_processData['results']['items']
    
    data = Tol_data(appointmentData, processData)
    
    
    print(f"\n[TolController]: [refresh]: {lastRefresh}")


async def auto_refresh():
    while True:
        await refresh(iWithLog=False)
        await asyncio.sleep(refreshDelay)

# async def dump_data():
    