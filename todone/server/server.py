import asyncio
import json
import signal
import sys

import websockets

from todone import response as resp
from todone.backend import transaction as trans
from todone.server import db


def signal_handler(signal, frame):
    """Perform any server-side cleanup after receiving SIGINT to exit"""
    print('\nExiting....')
    sys.exit(0)


async def transaction_server(websocket, path):
    msg = await websocket.recv()
    client, actions = json.loads(msg)
    for action in actions:
        action['client'] = client
    transactions = [trans.Transaction(**action)
                    for action in actions]
    for transaction in transactions:
        db.Transaction.new(transaction)
        print('>>>{}'.format(transaction))
    send_transactions = db.Client.sync(client)
    for t in send_transactions:
        print('<<<{}'.format(t))
    response = (resp.Response.SUCCESS, send_transactions)
    response_msg = json.dumps(response)
    await websocket.send(response_msg)


def main():
    signal.signal(signal.SIGINT, signal_handler)
    print('Todone server is listening on port 8765. Press CTRL-C to exit.')
    db.database.connect()
    db.database.create_tables([db.Client, db.Transaction])
    start_server = websockets.serve(transaction_server, 'localhost', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
