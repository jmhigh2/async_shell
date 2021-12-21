"""
python3.7 -m pip install aiohttp aiomultiprocessing
"""

from aiohttp import web
from aiohttp.web import WebSocketResponse
import aiohttp
import traceback
import json
import webbrowser
import importlib

CLIENTS = set()

port = 60000

# webbrowser.open("index.html")

async def broadcast(data):
    
    for ws in CLIENTS:
        try:
            await ws.send_str(data)

        except:
            CLIENTS.remove(ws)

async def websocket_handler(request):

    # our websocket can handle state
    ws = WebSocketResponse() 
    await ws.prepare(request)
    print(f"{request.headers['Host']} connected")

    CLIENTS.add(ws)

    # Since it's a persistent connection, every time there is a message sent it's processed below. The above
    # code is not run anymore. 
    async for msg in ws:

        if msg.type == aiohttp.WSMsgType.TEXT:
            data = msg.data
            try:
                args = json.loads(data)
            except:
                args = {}
            if "cmd" in args:
                importlib.invalidate_caches()
                try:
                    mod = importlib.import_module(f'commands.{args["cmd"]}')
                    mod = importlib.reload(mod)
                    main = getattr(mod, 'main')
                    stuff = await main("fake state")
                    await broadcast(stuff)

                except:
                    traceback.print_exc()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())            

        # await ws.send_str(f"Received at server: {data}")
        await broadcast(f"Broadcasted message: {data}")

    print(f"{request.headers['Host']} disconnected")

async def app_init():
    app = web.Application()

    app.add_routes([
        web.get('/ws', websocket_handler),
    ])
    return app 

if __name__ =="__main__":

    web.run_app(app_init(), host="0.0.0.0", port=port)