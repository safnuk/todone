import sys

import peewee

from todone.backends.db import (
    close_database,
    connect_database,
    initialize_database,
)
from todone.commands.folder import folder_command
from todone.commands.help import help_text
from todone.commands.list import list_items
from todone.commands.move import move_todo
from todone.commands.new import new_todo
from todone.commands.setup import setup_db, version
from todone.config import configure
from todone.parser.format import ApplyFunctionFormat
from todone.parser.match import (
    AlwaysMatch,
    FlagKeywordMatch,
    SubstringMatch,
)
from todone.parser.textparser import (
    ArgumentError,
    TextParser,
)

DB_HELP_MSG = """Cannot find valid database.

Make sure you have a valid configuration file:
    > todone help configure
then enter
    > todone setup
to initialize the database before using.
"""


class CommandDispatcher:
    DEFAULT_ARGS = ['help', ]

    def __init__(self, args):
        self.store_args(args)
        self.setup_parser()

    def store_args(self, args):
        if args:
            self.args = args
        else:
            self.args = (sys.argv[1:]
                         if len(sys.argv) > 1
                         else self.DEFAULT_ARGS)

    def setup_parser(self):
        self.parser = TextParser()
        self.parser.add_argument(
            'config', options=['-c', '--config'],
            match=FlagKeywordMatch, nargs='?',
            format=ApplyFunctionFormat,
            format_function=' '.join
        )
        self.parser.add_argument(
            'command', options=COMMAND_MAPPING,
            match=SubstringMatch,
            format=ApplyFunctionFormat,
            format_function=' '.join
        )
        self.parser.add_argument('args', nargs='*', match=AlwaysMatch)

    def parse_args(self):
        try:
            self.parser.parse(self.args)
        except ArgumentError:
            print('Invalid argument(s)')
            dispatch_command('help', ['--short'])
            raise SystemExit(1)

    def configure(self):
        configure(self.parser.parsed_data['config'])

    def dispatch_command(self):
        try:
            initialize_database()
            connect_database()
            dispatch_command(
                self.parser.parsed_data['command'],
                self.parser.parsed_data['args']
            )
            close_database()
        except peewee.OperationalError:
            print(DB_HELP_MSG)
            pass


def dispatch_command(action, args):
    try:
        COMMAND_MAPPING[action](args)
    except ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            action, e))
        COMMAND_MAPPING['help'](['--short', action])

COMMAND_MAPPING = {
    '-h': help_text,
    '--help': help_text,
    'help': help_text,
    '-v': version,
    '--version': version,
    'version': version,
    'folder': folder_command,
    'list': list_items,
    'move': move_todo,
    'new': new_todo,
    'setup': setup_db,
}
