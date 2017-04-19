"""Module containing commands for modifying folders in todone database.

Includes the subcommands:
    * ``new`` for creating new folders
    * ``rename`` for renaming a folder
    * ``delete`` for deleting a folder
"""
from todone import backend
from todone import exceptions

FOLDER_COMMANDS = ['new', 'rename', 'delete', 'list']
FOLDER_DISPATCH = {
    'new': backend.Folder.new,
    'rename': backend.Folder.rename,
    'delete': backend.Folder.remove,
    'list': lambda: print(
        '\n'.join(['{}/'.format(f.name) for f in backend.Folder.all()]))
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
    command = args['subcommand']
    folders = args['folders']
    if len(folders) < MIN_FOLDERS[command]:
        raise exceptions.ArgumentError(
            'Not enough folders provided (expected {})'.format(
                MIN_FOLDERS[command]
            )
        )
    elif len(folders) > MAX_FOLDERS[command]:
        raise exceptions.ArgumentError(
            'Too many folders provided'
        )
    FOLDER_DISPATCH[command](*folders)
    print(COMMAND_MESSAGE[command].format(*folders))


folder_command.short_help = """
usage todone folder <command> <args>
"""
