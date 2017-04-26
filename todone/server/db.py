"""Database schema for the cloud-based server in charge of syncing clients."""
import datetime
import json

import dateutil.parser
import peewee

database = peewee.SqliteDatabase(':memory:')


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Client(BaseModel):
    """
    Keep track of all client machines containing a copy of the database,
    and when they were last syned.
    """
    id = peewee.IntegerField(primary_key=True)
    last_sync = peewee.DateTimeField(default=datetime.datetime(2000, 1, 1))

    @classmethod
    def sync(cls, client_id):
        """Determine the list of transactions to be applied to the client
        machine to make its database consistent with the server's data.

        :param client_id: Key identifying the client who is attempting
            to sync with the server

        :returns: a list of transactions to send to the client
        """
        transactions = []
        client, _ = Client.get_or_create(id=client_id)
        query = Transaction.select().where(
            Transaction.client != client,
            Transaction.upload_time > client.last_sync
        ).order_by(Transaction.timestamp)
        for q in query:
            t = {}
            t['command'] = q.command
            t['timestamp'] = q.timestamp.isoformat()
            t['client'] = q.client.id
            t['args'] = json.loads(q.args)
            transactions.append(t)
        client.last_sync = datetime.datetime.now()
        client.save()
        return transactions


class Transaction(BaseModel):
    """
    Database table containing a complete history of all transactions
    applied to the database. Running through the transactions from
    earliest to latest should reproduce the current state of the
    database.
    """
    command = peewee.CharField()
    args = peewee.CharField()
    timestamp = peewee.DateTimeField()
    upload_time = peewee.DateTimeField(default=datetime.datetime.now)
    client = peewee.ForeignKeyField(Client, related_name='transactions')

    @classmethod
    def new(cls, transaction):
        Client.get_or_create(id=transaction.client)
        transaction.timestamp = dateutil.parser.parse(transaction.timestamp)
        transaction.args = json.dumps(transaction.args)
        trans = cls.create(**transaction.__dict__)
        print(trans)

    def __str__(self):
        return '({}, {}, {}, {}, {})'.format(self.command, self.timestamp,
                                             self.upload_time, self.client,
                                             self.args)
