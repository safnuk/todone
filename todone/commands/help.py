import textwrap

import todone.commands.dispatch
from todone.parser.factory import ParserFactory, PresetArgument


def help_text(args):
    """
    Command-line agenda and todo-list manager.

    usage: todone <command> [<args>]

    Allowed commands include:
        done        Move a todo to the done/ folder
        folder      Commands for manipulating folders (new, rename, delete)
        help        Display this help message
        list        Print a list of todos matching given search terms
        move        Move a todo to a new folder or project
        new         Add a new todo item
        setup       Create config file and initialize database
        version     Display version number

    See todone help <command> to read more about a specific command.
    """
    parsed_args = parse_args(args)
    command = parsed_args['command']

    if parsed_args['short']:
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


def parse_args(args):
    parser_initialization = [
        (PresetArgument.optional_switch,
         {'name': 'short',
          'options': ['-s', '--short'],
          'positional': False}),
        (PresetArgument.optional_switch,
         {'name': 'command',
          'options': todone.commands.dispatch.COMMAND_MAPPING}),
    ]
    parser = ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data


help_text.short_general_help = """
usage: todone <command> [args]

Allowed commands include: help, list, new, setup, version.

Type "todone help <command>" to read more about a specific command.
"""

help_text.short_help = """
usage todone help [command]

Allowed commands include: help, list, new, setup, version.
"""
