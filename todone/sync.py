import asyncio
import websockets

from todone import backend
from todone import config


class Sync:
    def run(self):
        asyncio.get_event_loop().run_until_complete(self.send_transactions())

    async def send_transactions(self):
        url = config.settings['master']['url']
        async with websockets.connect(url) as websocket:
            unsynced = backend.UnsyncedQueue.all_as_json()
            await websocket.send(unsynced)
            print('>>>>>>>>>>>>>>>>>>>>>>>>>')
            print(unsynced)
            print('<<<<<<<<<<<<<<<<<<<<<<<<<<')

            response = await websocket.recv()
            print(response)
