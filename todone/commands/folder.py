import peewee

from todone.backends.db import Folder, Todo
from todone import config
from todone.textparser import (
    AlwaysMatch,
    ApplyFunctionFormat,
    ArgumentError,
    SubstringMatch,
    TextParser,
)

FOLDER_COMMANDS = ['new', 'rename', 'delete', 'list']


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
        if not parsed_args['folders']:
            raise ArgumentError(
                'No folder name specified'
            )
        for folder in parsed_args['folders']:
            try:
                Folder.create(name=folder)
                print('Added folder: {}/'.format(folder))
            except peewee.IntegrityError:
                raise ArgumentError(
                    'Folder {}/ already exists'.format(folder))
    elif parsed_args['command'] == 'rename':
        if len(parsed_args['folders']) > 2:
            raise ArgumentError(
                'Too many folder arguements for rename (2 expected)'
            )
        try:
            old_folder_name = parsed_args['folders'][0]
            new_folder_name = parsed_args['folders'][1]
        except IndexError:
            raise ArgumentError(
                'Not enough folder arguments for rename (2 expected)'
            )
        try:
            old_folder = Folder.get(Folder.name == old_folder_name)
        except peewee.DoesNotExist:
            raise ArgumentError(
                'No match found for folder {}/'.format(old_folder_name)
            )
        try:
            new_folder = Folder.create(name=new_folder_name)
        except peewee.IntegrityError:
            raise ArgumentError(
                'Folder {}/ already exists'.format(new_folder_name))
        query = Todo.update(folder=new_folder).where(
            Todo.folder == old_folder
        )
        query.execute()
        old_folder.delete_instance()
        print('Renamed folder: {}/ -> {}/'.format(
            old_folder_name, new_folder_name))
    elif parsed_args['command'] == 'delete':
        if len(parsed_args['folders']) != 1:
            raise ArgumentError(
                'Expected one folder to delete, found {}'.format(
                    len(parsed_args['folders'])
                )
            )
        try:
            folder_name = parsed_args['folders'][0]
            folder = Folder.get(Folder.name == folder_name)
        except peewee.DoesNotExist:
            raise ArgumentError(
                'Folder {} does not exist'.format(folder_name)
            )
        query = Todo.update(
            folder=config.settings['folders']['default_inbox']
        ).where(Todo.folder == folder)
        query.execute()
        folder.delete_instance()
        print('Deleted folder: {}/'.format(folder_name))
    elif parsed_args['command'] == 'list':
        if parsed_args['folders']:
            raise ArgumentError(
                'list command does not accept arguments'
            )
        for folder in Folder.select():
            print('{}/'.format(folder.name))


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
        nargs='*',
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
