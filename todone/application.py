import sys

import peewee

from todone.backends.db import (
    close_database,
    connect_database,
    initialize_database,
)
from todone.commands.dispatch import COMMAND_MAPPING, dispatch_command
from todone.config import configure
from todone.textparser import (
    AlwaysMatch,
    ApplyFunctionFormat,
    ArgumentError,
    FlagKeywordMatch,
    SubstringMatch,
    TextParser,
)

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(cli_args=None):
    if cli_args is None:
        cli_args = sys.argv[1:] if len(sys.argv) > 1 else ['help']

    parser = TextParser()
    parser.add_argument(
        'config', options=['-c', '--config'],
        match=FlagKeywordMatch, nargs='?',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument(
        'command', options=COMMAND_MAPPING,
        match=SubstringMatch,
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument('args', nargs='*', match=AlwaysMatch)

    try:
        parser.parse(cli_args)
    except ArgumentError:
        print('Invalid argument(s)')
        dispatch_command('help', ['--short'])
        return 1

    configure(parser.parsed_data['config'])
    try:
        initialize_database()
        connect_database()
        dispatch_command(
            parser.parsed_data['command'],
            parser.parsed_data['args']
        )
        close_database()
    except peewee.OperationalError:
        print(DB_HELP_MSG)

DB_HELP_MSG = """Cannot find valid database.

Make sure you have a valid configuration file:
    > todone help configure
then enter
    > todone setup
to initialize the database before using.
"""
