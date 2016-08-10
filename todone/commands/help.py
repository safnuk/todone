import textwrap

import todone.commands.dispatch
from todone.parser.textparser import ApplyFunctionFormat, TextParser


def help_text(args):
    """
    Command-line agenda and todo-list manager.

    usage: todone <command> [<args>]

    Allowed commands include:
        help    Display this help message
        list    Print a list of todos matching given search terms
        new     Add a new todo item
        setup   Configure database
        version Display version number

    See todone help <command> to read more about a specific command.
    """
    parser = TextParser()
    parser.add_argument(
        'short', options=['-s', '--short'],
        nargs='?', positional=False,
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument(
        'command', options=todone.commands.dispatch.COMMAND_MAPPING,
        nargs='?',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.parse(args)
    command = parser.parsed_data['command']

    if parser.parsed_data['short']:
        if command:
            print(todone.commands.dispatch.COMMAND_MAPPING[command].short_help)
        else:
            print(help_text.short_general_help)
    else:
        command = command if command else 'help'
        print(
            textwrap.dedent(
                todone.commands.dispatch.COMMAND_MAPPING[command].__doc__
            )
        )

help_text.short_general_help = """
usage: todone <command> [args]

Allowed commands include: help, list, new, setup, version.

Type "todone help <command>" to read more about a specific command.
"""

help_text.short_help = """
usage todone help [command]

Allowed commands include: help, list, new, setup, version.
"""
