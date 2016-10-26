import peewee

from todone.backends.db import create_database
from todone import config
from todone.config import save_configuration, VERSION
from todone.parser.factory import ParserFactory, PresetArgument
from todone.parser.textparser import ArgumentError


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
            save_configuration()
            print("Created basic config file '{}'".format(config.config_file))
        try:
            create_database()
            print("New todone database initialized at '{}'".format(
                config.settings['database']['name']
            ))
        except peewee.OperationalError:
            print('Database has already been setup - get working!')

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
        print('Todone {}'.format(VERSION))
    else:
        raise ArgumentError()

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
        raise ArgumentError()
    Setup.dispatch(command, remaining_args)

setup_db.short_help = """
usage: todone setup init
"""


def parse_args(args=[]):
    argtypes = [
        (PresetArgument.required_switch,
         {'name': 'command', 'options': Setup.COMMANDS}),
        (PresetArgument.all_remaining,
         {'name': 'args', }),
    ]
    parser = ParserFactory.from_arg_list(argtypes)
    parser.parse(args)
    return parser.parsed_data
