import peewee

from todone.backends.db import create_database
from todone.config import VERSION
from todone.textparser import ArgumentError


def version(args=[]):
    if not args:
        print('Todone {}'.format(VERSION))
    else:
        raise ArgumentError()


def setup_db(args=[]):
    if not args:
        try:
            create_database()
            print('New todone database initialized')
        except peewee.OperationalError:
            print('Database has already been setup - get working!')
    else:
        raise ArgumentError()
