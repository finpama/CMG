from fastapi import FastAPI
from contextlib import asynccontextmanager

import asyncio
import requests as req
import json

from datetime import datetime

lastRefresh = datetime.now()
refreshDelay = 60 * 2 #Em segundos

async def requestToken() -> str:
    with open('./cmg/password.json') as pw:
        jsonPW = json.loads(pw.read())

    response = req.post('https://purcell.terminalonline.com.br/authenticate', json=jsonPW)

    data = json.loads(response.content)
    data_results = data.get('results')
    TOKEN = data_results.get('token')
    
    return TOKEN

async def refresh():
    global lastRefresh
    lastRefresh = datetime.now()
    
    TOKEN = await requestToken()
    
    print(f"     [refresh]: {lastRefresh}")
    print(TOKEN)
    
async def run_refresh():
    while True:
        await refresh()
        await asyncio.sleep(refreshDelay)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup:
    print('     [lifespan]: running startup')
    asyncio.create_task(run_refresh())
    
    yield
    # shutdown:
    print('     [lifespan]: running shutdown')
    
    


app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_status():
    return {"last_refresh": lastRefresh}

@app.get("/refresh")
async def re():
    await refresh()
    return {"new_re": lastRefresh}