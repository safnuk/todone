from todone.backends.db import create_tables
from todone.config import VERSION
from todone.textparser import ArgumentError


def version(args=[]):
    if not args:
        print('Todone {}'.format(VERSION))
    else:
        raise ArgumentError()


def setup_db(args=[]):
    if not args:
        create_tables()
    else:
        raise ArgumentError()
