import datetime

from todone.backends.db import ListItem, SavedList, Todo, MOST_RECENT_SEARCH
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

    Usage: todone list [.file] [folder] [tags and keywords]

    Search criteria can be any string expression.

    Allowed folder keywords are: today, next, inbox, project,
    cal[-N{d|w|m|y}][+N{d|w|m|y}], someday, done. Shortened
    versions accepted when unambiguous, so, for example "done", "don",
    and "do" all indicate the done folder (d defaults to the "due" tag).
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
    [Folder name] or [N] where N is the number associated to the
    project. This can be obtained by typing
        todone list project

    The remainder of the search string provides keywords that must
    appear in the todo title. However, searches are always case
    insensitive.

    If any keyword begins with '~', then the search limits to items
    that do not contain the given item

    If .file is specified, then search results are saved to .file.
    Otherwise, the default file is .todos.

    If no search criteria is provided, then the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently used search is used.

    E.g.,
        > todone list .my_search today @Work
            Lists all today items containing tag @Work
        > todone list n due+1w [My Project]
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
    empty_args = True
    for key, value in parsed_args.items():
        if value:
            empty_args = False
            break
    if empty_args:
        query = [item.todo for item in SavedList.get_most_recent().items]
    else:
        query = Todo.select()
        if parsed_args['folder']:
            if parsed_args['folder'] in settings['folders']['today']:
                query = query.where(
                    (Todo.folder == parsed_args['folder']) |
                    (Todo.due <= datetime.date.today()) |
                    (Todo.remind <= datetime.date.today())
                ).where(~(Todo.folder << settings['folders']['inactive']))
            else:
                query = query.where(Todo.folder == parsed_args['folder'])
        else:
            query = Todo.active_todos()
        if parsed_args['due']:
            query = query.where(Todo.due <= parsed_args['due'])
        if parsed_args['remind']:
            query = query.where(Todo.remind <= parsed_args['remind'])
        for keyword in parsed_args['keywords']:
            query = query.where(Todo.action.contains(keyword))
        save_most_recent_search(query)
    for todo in query:
        print_todo(todo)


def save_most_recent_search(query):
    recent, _ = SavedList.get_or_create(name=MOST_RECENT_SEARCH)
    old_list = ListItem.delete().where(ListItem.savedlist == recent)
    old_list.execute()
    for todo in query:
        ListItem.create(savedlist=recent, todo=todo)


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
