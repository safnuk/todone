import peewee

from todone.backends.db import create_database
from todone.config import VERSION
from todone.parser.factory import ParserFactory, PresetArgument
from todone.parser.textparser import ArgumentError


class Setup:
    COMMANDS = ['init']

    @classmethod
    def dispatch(cls, command, args):
        DISPATCH = {
            'init': cls.initialize,
        }
        DISPATCH[command](*args)

    @classmethod
    def initialize(cls):
        try:
            create_database()
            print('New todone database initialized')
        except peewee.OperationalError:
            print('Database has already been setup - get working!')


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
