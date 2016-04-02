import peewee

from todone.backends.db import Folder
from todone.textparser import (
    AlwaysMatch,
    ApplyFunctionFormat,
    ArgumentError,
    SubstringMatch,
    TextParser,
)

FOLDER_COMMANDS = ['new', 'rename', 'delete']


def folder_command(args):
    """
    Edit the folder structure of the todo list.

    usage: todone folder <command> <folder(s)>

    Valid commands are:

        new    create a new folder with the given name
        rename rename an existing folder
        delete remove a folder
    """
    parsed_args = parse_args(args)
    if parsed_args['command'] == 'new':
        for folder in parsed_args['folders']:
            try:
                Folder.create(name=folder)
                print('Added folder: {}/'.format(folder))
            except peewee.IntegrityError:
                raise ArgumentError(
                    'Folder {}/ already exists'.format(folder))
    # elif parsed_args['command'] == 'rename':
    #     f = Folder.get(Folder.name == parsed_args['folders'][0])
    #     f.name = parsed_args['folders'][1]
    #     f.save()


folder_command.short_help = """
usage todone folder <command> <args>
"""


def parse_args(args=[]):
    parser = TextParser()
    parser.add_argument(
        'command',
        options=FOLDER_COMMANDS,
        match=SubstringMatch,
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument(
        'folders',
        nargs='+',
        match=AlwaysMatch,
        format=ApplyFunctionFormat,
        format_function=_strip_trailing_slash
    )
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
