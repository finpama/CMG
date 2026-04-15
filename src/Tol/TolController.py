import asyncio
import requests as req
import json

from datetime import datetime, timedelta

from ..config_reader import read_configFile
from ..Database import dbController, dbModel

# delay de atualização em segundos
hour = read_configFile('tolController', 'refreshDelayHours')
refreshDelay = 60 * 60 * hour  # --> horas

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


async def refresh():
    lastRefresh = datetime.now()
    
    TOL_appointmentData = appointmentRequest(Session).json()
    TOL_processData = processRequest(Session).json()
    
    appointmentData = json.dumps(TOL_appointmentData['results'])
    processData = json.dumps(TOL_processData['results']['items'])
    
    dados = dbModel.Dados_tol(
        data_refresh = lastRefresh,
        dados_agendamento = appointmentData,
        dados_processos = processData,
    )
    
    insertDados_task = asyncio.create_task(dbController.insert_dados_tol(dados))
    await insertDados_task
    
    insertDados_taskResult = insertDados_task.result()
    
    if insertDados_taskResult == 0 :
        print(f"\n[TolController]: successfuly refreshed at: {lastRefresh}")
    else:
        print(f"\n[TolController]: failed refreshing at: {lastRefresh}. Error below:\n")
        print(insertDados_taskResult.args[0])


async def auto_refresh():
    # on startup
    selectLastRefresh_task = asyncio.create_task(dbController.selectById_dados_tol('latest'))
    await selectLastRefresh_task
    selectLastRefresh_taskResult = selectLastRefresh_task.result()
    
    global lastRefresh
    
    if isinstance(selectLastRefresh_taskResult, dbController.IntegrityError):
        
        print(f"\n[TolController]: refreshing now: failed getting lastRefresh in database. Error:")
        print(selectLastRefresh_taskResult)
        
        lastRefresh = datetime.now() - timedelta(days=1) # define o lastRefresh em memória para um dia atrás, forçando o refresh
        
    elif isinstance(selectLastRefresh_taskResult, dbModel.Dados_tol):
        
        lastRefresh = selectLastRefresh_taskResult.data_refresh
        
        if lastRefresh != None:
            print(f"\n[TolController]: successfuly got lastRefresh in database: {lastRefresh}")
        else:
            print(f"\n[TolController]: 0 refreshes found in database. Refreshing now...")
            lastRefresh = datetime.now() - timedelta(days=1) # define o lastRefresh em memória para um dia atrás, forçando o refresh
        
        
    else:
        lastRefresh = selectLastRefresh_taskResult[1]
        
        if lastRefresh != None:
            print(f"\n[TolController]: successfuly got lastRefresh in database: {lastRefresh}")
        else:
            print(f"\n[TolController]: 0 refreshes found in database. Refreshing now...")
            lastRefresh = datetime.now() - timedelta(days=1) # define o lastRefresh em memória para um dia atrás, forçando o refresh
        
    
    # runs until shutdown
    while True:
        if lastRefresh <= (datetime.now() - timedelta(seconds=refreshDelay)):
            await refresh()
            
        await asyncio.sleep(refreshDelay)

