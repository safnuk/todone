"""Module containing commands for modifying folders in todone database.

Includes the subcommands:
    * ``new`` for creating new folders
    * ``rename`` for renaming a folder
    * ``delete`` for deleting a folder
"""
from todone.parser import factory

FOLDER_COMMANDS = ['new', 'rename', 'delete', 'list']


def parse_args(args=[]):
    arglist = [
        (factory.PresetArgument.required_switch,
         {'name': 'subcommand', 'options': FOLDER_COMMANDS}),
        (factory.PresetArgument.all_remaining,
         {'name': 'folders', 'format_function': _strip_trailing_slash}),
    ]
    parser = factory.ParserFactory.from_arg_list(arglist)
    parser.parse(args)
    return parser.parsed_data


def _strip_trailing_slash(args):
    formatted = []
    for arg in args:
        if arg[-1] == '/':
            formatted.append(arg[:-1])
        else:
            formatted.append(arg)
    return formatted
