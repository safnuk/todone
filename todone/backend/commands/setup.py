"""Module for creating a configuration file (if necessary) and initializing
the database.
"""
from todone import backend
from todone import config
from todone import __version__
from todone import exceptions


class Setup:
    COMMANDS = ['init']
    DEFAULT_DB = '~/.todone.sqlite'

    @classmethod
    def dispatch(cls, command, args=[]):
        DISPATCH = {
            'init': cls.initialize,
        }
        DISPATCH[command](*args)

    @classmethod
    def initialize(cls):
        if not config.settings['database']['name']:
            config.settings['database']['name'] = cls.query_user_for_db_name()
            config.save_configuration()
            backend.Database.update()
            print("Created basic config file '{}'".format(config.config_file))
        try:
            backend.Database.create()
            print("New todone database initialized at '{}'".format(
                config.settings['database']['name']
            ))
        except backend.DatabaseError as e:
            if "already exists" in str(e):
                print('Database has already been setup - get working!')
            else:
                raise e

    @classmethod
    def query_user_for_db_name(cls):
        name = cls.get_input()
        return name if name else cls.DEFAULT_DB

    @classmethod
    def get_input(cls):
        query = "Enter location of database ['{}']: ".format(cls.DEFAULT_DB)
        return input(query).strip()


def version(args):
    """
    Display version information.

    usage: todone version

    Note that "todone -v" and "todone --version" are also acceptable.

    """
    if not args:
        print('Todone {}'.format(__version__))
    else:
        raise exceptions.ArgumentError()

version.short_help = """
usage: todone version
"""


def setup_db(args):
    """
    Create a basic configuration file (if needed), based on user input, and
    initializes a new, empty database (if one does not exist).

    usage: todone setup init
    """
    command = args['subcommand']
    Setup.dispatch(command)

setup_db.short_help = """
usage: todone setup init
"""
