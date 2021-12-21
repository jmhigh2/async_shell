"""
python3.7 -m pip install aiohttp aiomultiprocessing ptpython aioconsole
"""

import os
from aiohttp import web
from aiohttp.web import WebSocketResponse
import aiohttp
import traceback
import json
import webbrowser
import asyncio
import importlib
from ptpython.repl import embed

CLIENTS = set()


loop = asyncio.get_event_loop()


def handler(loop, context):

    if "KeyboardInterrupt" in  str(context["exception"]):
        pass
    else:
        print(context["exception"])

loop.set_exception_handler(handler)

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
                    main = globals()[args["cmd"]]
                    stuff = await main("fake state")
                    await broadcast(stuff)

                except:
                    traceback.print_exc()

        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' % ws.exception())            

        # await ws.send_str(f"Received at server: {data}")
        await broadcast(f"Broadcasted message: {data}")

    print(f"{request.headers['Host']} disconnected")

def reload():

    commands = [f for f in os.listdir("commands") if os.path.isfile(os.path.join("commands", f))]
    for file in commands:

        mod = importlib.import_module(f"commands.{file.replace('.py', '')}")
        mod = importlib.reload(mod)
        main = getattr(mod, 'main')
        globals()[file.replace('.py', '')] = main # yolo

def configure(repl):

    repl.confirm_exit = False

async def interactive_shell(app):
    """
    Coroutine that starts a Python REPL from which we can access everything
    """

    reload()
    try:
        await embed(globals=globals(), return_asyncio_coroutine=True, patch_stdout=True, vi_mode=True, configure=configure)
        
    except EOFError:
        print("here1")
        
        raise KeyboardInterrupt
    loop.stop()
    raise KeyboardInterrupt

async def startup(app):

    app["shell"] = asyncio.create_task(interactive_shell(app))

async def app_init():
    
    app = web.Application()
    app.on_startup.append(startup)

    app.add_routes([
        web.get('/ws', websocket_handler),
    ])
    return app 

if __name__ =="__main__":
    
    web.run_app(app_init(), host="0.0.0.0", port=port, loop=loop, print=False)