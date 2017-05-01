import asyncio
import json
import websockets

from todone import backend
from todone.backend import commands as cmd
from todone.backend import transaction as trans
from todone import config
from todone import response as resp


class Sync:
    def run(self):
        try:
            backend.Database.connect()
            asyncio.get_event_loop().run_until_complete(
                self.send_transactions())
            backend.Database.close()
        except OSError:
            return []
        except backend.DatabaseError:
            return []
        return self.messages

    async def send_transactions(self):
        url = config.settings['master']['url']
        async with websockets.connect(url) as websocket:
            unsynced = backend.UnsyncedQueue.all_as_json()
            msg = '[{}, {}]'.format(backend.Client.get_client_id(), unsynced)
            await websocket.send(msg)
            self.response = await websocket.recv()
            self.handle_response()

    def handle_response(self):
        code, actions = json.loads(self.response)
        messages = []
        if code == resp.Response.SUCCESS:
            transactions = [trans.Transaction(**action)
                            for action in actions]
            for transaction in transactions:
                cmd_class = cmd.COMMAND_MAPPING[transaction.command]
                msg = cmd_class.apply(transaction, [backend.UndoStack])
                if type(msg) == resp.Response:
                    messages.append(msg)
                if type(msg) == list:
                    messages += msg
            backend.UnsyncedQueue.clear()
        self.messages = messages
