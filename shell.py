import aiohttp
import asyncio
import aioconsole
import json

async def listener(ws):

    await ws.send_str("hello")
    async for msg in ws:

        print(msg.data)


async def console(ws):

    while True:
        # make some kind of ready flag
        data = await aioconsole.ainput()

        if data:
            payload = json.dumps({"cmd": data})
            await ws.send_str(payload)

async def main():

    async with aiohttp.ClientSession().ws_connect('http://localhost:60000/ws') as ws:
        print("Connected!")
        a = listener(ws)
        b = console(ws)

        await asyncio.gather(*[a, b])
    
loop = asyncio.get_event_loop()
loop.run_until_complete(main())