from todone.backends.db import Folder
from todone.parser.factory import ParserFactory, PresetArgument
from todone.parser.textparser import ArgumentError

FOLDER_COMMANDS = ['new', 'rename', 'delete', 'list']
FOLDER_DISPATCH = {
    'new': Folder.safe_new,
    'rename': Folder.safe_rename,
    'delete': Folder.safe_delete,
    'list': Folder.list
}

COMMAND_MESSAGE = {
    'new': 'Added folder: {}/',
    'rename': 'Renamed folder: {}/ -> {}/',
    'delete': 'Deleted folder: {}/',
    'list': '',
}

MIN_FOLDERS = {
    'new': 1,
    'rename': 2,
    'delete': 1,
    'list': 0,
}

MAX_FOLDERS = {
    'new': 1,
    'rename': 2,
    'delete': 1,
    'list': 0,
}


def folder_command(args):
    """
    Edit the folder structure of the todo list.

    usage: todone folder <command> <folder(s)>

    Valid commands are:

        new    create a new folder with the given name
        rename rename an existing folder
        delete remove a folder
        list   list all folders
    """
    parsed_args = parse_args(args)
    command = parsed_args['command']
    folders = parsed_args['folders']
    if len(folders) < MIN_FOLDERS[command]:
        raise ArgumentError(
            'Not enough folders provided (exptected {})'.format(
                MIN_FOLDERS[command]
            )
        )
    elif len(folders) > MAX_FOLDERS[command]:
        raise ArgumentError(
            'Too many folders provided'
        )
    FOLDER_DISPATCH[command](*folders)
    print(COMMAND_MESSAGE[command].format(*folders))


folder_command.short_help = """
usage todone folder <command> <args>
"""


def parse_args(args=[]):
    arglist = [
        (PresetArgument.required_switch,
         {'name': 'command', 'options': FOLDER_COMMANDS}),
        (PresetArgument.all_remaining,
         {'name': 'folders', 'format_function': _strip_trailing_slash}),
    ]
    parser = ParserFactory.from_arg_list(arglist)
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
