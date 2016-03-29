import peewee

from todone.backends.db import create_database
from todone.config import VERSION
from todone.textparser import ArgumentError


def version(args=[]):
    """
    Display version information.

    usage: todone version

    Note that "todone -v" and "todone --version" are also acceptable.

    """
    if not args:
        print('Todone {}'.format(VERSION))
    else:
        raise ArgumentError()

version.short_help = """
usage: todone version
"""


def setup_db(args=[]):
    """
    Performs initial setup of database specified by configuration file.

    usage: todone setup
    """
    if not args:
        try:
            create_database()
            print('New todone database initialized')
        except peewee.OperationalError:
            print('Database has already been setup - get working!')
    else:
        raise ArgumentError()

setup_db.short_help = """
usage: todone setup
"""