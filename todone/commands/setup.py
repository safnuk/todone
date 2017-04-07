"""Module for creating a configuration file (if necessary) and initializing
the database.
"""
from todone import backend, config, __version__
from todone.parser import factory
from todone.parser import exceptions as pe


class Setup:
    COMMANDS = ['init']
    DEFAULT_DB = '~/.todone.sqlite'

    @classmethod
    def dispatch(cls, command, args):
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


def version(args=[]):
    """
    Display version information.

    usage: todone version

    Note that "todone -v" and "todone --version" are also acceptable.

    """
    if not args:
        print('Todone {}'.format(__version__))
    else:
        raise pe.ArgumentError()

version.short_help = """
usage: todone version
"""


def setup_db(args=[]):
    """
    Create a basic configuration file (if needed), based on user input, and
    initializes a new, empty database (if one does not exist).

    usage: todone setup init
    """
    parsed_args = parse_args(args)
    command = parsed_args['command']
    remaining_args = parsed_args['args']
    if remaining_args:
        raise pe.ArgumentError()
    Setup.dispatch(command, remaining_args)

setup_db.short_help = """
usage: todone setup init
"""


def parse_args(args=[]):
    argtypes = [
        (factory.PresetArgument.required_switch,
         {'name': 'command', 'options': Setup.COMMANDS}),
        (factory.PresetArgument.all_remaining,
         {'name': 'args', }),
    ]
    parser = factory.ParserFactory.from_arg_list(argtypes)
    parser.parse(args)
    return parser.parsed_data
