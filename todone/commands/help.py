import textwrap

import todone
from todone.textparser import ApplyFunctionFormat, TextParser


def help_text(args):
    """
    Command-line agenda and todo-list manager.

    usage: todone [--version] [--help] <command> [<args>]

    Allowed commands include:
        help    Display this help message
        list    Print a list of todos matching given search terms
        new     Add a new todo item
        setup   Configure database

    See todone help <command> to read more about a specific command.
    """
    parser = TextParser()
    parser.add_argument(
        'command', options=todone.commands.COMMAND_MAPPING,
        nargs='?',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.parse(args)
    command = (
        parser.parsed_data['command']
        if parser.parsed_data['command'] else 'help'
    )
    print(textwrap.dedent(todone.commands.COMMAND_MAPPING[command].__doc__))
