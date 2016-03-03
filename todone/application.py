import sys

from todone.commands import COMMAND_MAPPING, dispatch
from todone.textparser import (
    AlwaysMatch,
    ApplyFunctionFormat,
    SubstringMatch,
    TextParser,
)

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(cli_args=None):
    parsed = {
        'command': None,
        'args': [],
    }
    if cli_args is None:
        cli_args = sys.argv[1:] if len(sys.argv) > 1 else ['help']

    parser = TextParser()
    parser.add_argument(
        'command', options=COMMAND_MAPPING,
        match=SubstringMatch,
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument('args', nargs='*', match=AlwaysMatch)
    parser.parse(cli_args)
    parsed.update(parser.parsed_data)

    dispatch(parsed['command'], parsed['args'])
