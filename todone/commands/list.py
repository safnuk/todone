import datetime

from todone.backends.db import SavedList, Todo
from todone.commands.constants import DUE_REGEX, REMIND_REGEX
from todone.config import settings
from todone.printers import print_todo
from todone.textparser import (
    AlwaysMatch,
    ApplyFunctionFormat,
    DateFormat,
    FolderMatch,
    RegexMatch,
    TextParser,
)


def list_items(args):
    """
    Print a list of todos matching given search terms.

    usage: todone list [.file] [folder/] [tags and keywords]

    Search criteria can be any string expression.

    Allowed folder keywords are: today, next, inbox, project,
    cal[-N{d|w|m|y}][+N{d|w|m|y}], someday, done. Shortened
    versions accepted when unambiguous, so, for example "done", "don",
    "do", and "d" all indicate the done folder.
    If folder is not specified, the default is to search all active
    folders (inbox, next, today).
    The date specification for cal items limits to items with
    a date within the specified time interval, where -N{d|w|m|y}
    sets a lower bound on allowed dates (shift from today by
    given amount) and +N{d|w|m|y} sets an upper bound.

    If folder is "today", then, in addition to items in the today
    folder, items with a reminder or due date prior to or equal to
    today's date are also included.

    Allowed tags are:

    due[+N{d|w|m|y}],
    remind[+N{d|w|m|y}],
    [project name] or [N] where N is the number associated to the
    project. This can be obtained by typing
        todone list project

    The remainder of the search string provides keywords that must
    appear in the todo title. However, searches are always case
    insensitive.

    If any keyword begins with '~', then the search limits to items
    that do not contain the given item

    If .file is specified, then search results are saved to .file.

    If no search criteria is provided, then the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently run search is repeated.

    E.g.,
        > todone list .my_search today/ @Work
            Lists all today items containing tag @Work
        > todone list n/due+1w [My Project]
            Lists all next items from project [My Project] due in
            the next week
        > todone list
            Repeats most recent search
        > todone list .my_search
            Repeats list from first search
        > todone list
            Repeats list from first search
        > todone list r+5d "(foo | baz)"
            List all upcoming reminders (in next 5 days) containing
            foo or baz. Quotes are needed to avoiding shell escaping
            special characters.
    """
    parsed_args = parse_args(args)
    if is_loading_saved_search(parsed_args):
        query = SavedList.get_todos_in_list(parsed_args['file'])
    else:
        query = construct_query_from_argdict(parsed_args)
        SavedList.save_search(parsed_args['file'], query)
    SavedList.save_most_recent_search(query)
    for n, todo in enumerate(query):
        print_todo(n+1, todo)

list_items.short_help = """
usage: todone list [.file] [folder/] [tags and keywords]
"""


def construct_query_from_argdict(args):
    query = Todo.select()
    if args['folder']:
        if args['folder'] in settings['folders']['today']:
            query = query.where(
                (Todo.folder == args['folder']) |
                (Todo.due <= datetime.date.today()) |
                (Todo.remind <= datetime.date.today())
            ).where(~(Todo.folder << settings['folders']['inactive']))
        else:
            query = query.where(Todo.folder == args['folder'])
    else:
        query = Todo.active_todos()
    if args['due']:
        query = query.where(Todo.due <= args['due'])
    if args['remind']:
        query = query.where(Todo.remind <= args['remind'])
    for keyword in args['keywords']:
        query = query.where(Todo.action.contains(keyword))
    return query


def is_loading_saved_search(args):
    for key, value in args.items():
        if (key != 'file') and value:
            return False
    return True


def parse_args(args=[]):
    parser = TextParser()
    parser.add_argument(
        'file', options=[r'\.(?P<file>.+)', ],
        match=RegexMatch, nargs='?',
        format_function=_get_file_name,
        format=ApplyFunctionFormat
    )
    parser.add_argument(
        'folder', options=settings['folders']['default_folders'],
        match=FolderMatch, nargs='?',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.add_argument(
        'due', options=DUE_REGEX, match=RegexMatch,
        format=DateFormat, nargs='?',
        positional=False
    )
    parser.add_argument(
        'remind', options=REMIND_REGEX, match=RegexMatch,
        format=DateFormat, nargs='?',
        positional=False
    )
    parser.add_argument(
        'keywords', match=AlwaysMatch,
        nargs='*'
    )
    parser.parse(args)
    return parser.parsed_data


def _get_file_name(x):
    if x:
        return x[0].group('file')
    return None
