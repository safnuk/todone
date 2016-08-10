from todone.backends.db import SavedList
from todone.config import settings
from todone.parser.format import ApplyFunctionFormat
from todone.parser.match import (
    FolderMatch,
    RegexMatch,
)
from todone.parser.textparser import TextParser


def move_todo(args):
    """Move a todo from most recent search to a new folder or project.

    usage: todone move N folder/
           todone move N [project]

    """
    parsed_args = parse_args(args)
    todos = SavedList.get_todos_from_most_recent_search()
    target = todos[parsed_args['index']-1]
    target.folder = parsed_args['folder']
    target.save()
    print('Moved: "{}" to {}'.format(target.action, target.folder.name))

move_todo.short_help = """
usage: todone move N folder/
       todone move N [project]
where N is the number of the todo referenced in most recent search.
"""


def parse_args(args):
    parser = TextParser()
    parser.add_argument(
        'index', options=[r'(?P<index>\d+)', ],
        match=RegexMatch, nargs=1,
        format_function=_get_index,
        format=ApplyFunctionFormat
    )
    parser.add_argument(
        'folder', options=settings['folders']['default_folders'],
        match=FolderMatch, nargs='?',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.parse(args)
    return parser.parsed_data


def _get_index(arg):
    if arg:
        return int(arg[0].group('index'))
    return None
