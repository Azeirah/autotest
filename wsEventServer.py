import asyncio
import websockets
import threading
import functools
import json

async def queue_notifier(websocket, path, evt_queue):
    print('new connection!')

    try:
        while True:
            evt = await evt_queue.get()
            await websocket.send(json.dumps(evt))
    finally:
        print('connection died!')

def __run_ws_event_server(evt_queue, evt_loop):
    bound_handler = functools.partial(queue_notifier, evt_queue=evt_queue)
    asyncio.set_event_loop(evt_loop)
    evt_loop.run_until_complete(
        websockets.serve(bound_handler, 'localhost', 6789))
    evt_loop.run_forever()

def start_server(evt_loop):
    evt_queue = asyncio.Queue()

    t = threading.Thread(target=__run_ws_event_server, args=(evt_queue, evt_loop))
    t.start()

    return evt_queue


