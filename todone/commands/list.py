import datetime
from dateutil.relativedelta import relativedelta
import re

from todone.backends import folders
from todone.backends.db import Todo
from todone.printers import print_todo


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
    if not args:
        for todo in Todo.select().where(Todo.folder == folders.TODAY):
            print_todo(todo)
        return
    parsed_args = parse_args(args)
    query = Todo.select()
    if parsed_args['folder']:
        if parsed_args['folder'] == folders.TODAY:
            query = query.where(
                (Todo.folder == folders.TODAY) |
                (Todo.due_date <= datetime.date.today()) |
                (Todo.remind_date <= datetime.date.today())
            ).where(~(Todo.folder << [folders.DONE, folders.CANCEL]))
        else:
            query = query.where(Todo.folder == parsed_args['folder'])
    else:
        query = Todo.active_todos()
    if parsed_args['due']:
        query = query.where(Todo.due_date <= parsed_args['due'])
    if parsed_args['remind']:
        query = query.where(Todo.remind_date <= parsed_args['remind'])
    for keyword in parsed_args['keywords']:
        query = query.where(Todo.action.contains(keyword))
    for todo in query:
        print_todo(todo)


def parse_args(args=[]):
    parsed = {
        'file': None,
        'folder': None,
        'due': None,
        'remind': None,
        'keywords': [],
    }
    try:
        if args[0][0] == '.':
            parsed['file'] = args[0]
            args = args[1:]
        parsed['folder'] = parse_folder(args[0])
        if parsed['folder']:
            args = args[1:]
    except IndexError:
        pass
    for arg in args:
        key, value = parse_keyword(arg)
        if key:
            parsed[key] = value
        else:
            parsed['keywords'].append(arg)
    return parsed


def parse_folder(arg):
    if not arg:
        return None
    regex = re.compile('^' + arg, re.IGNORECASE)
    for folder in [x for x in folders.FOLDERS if x is not folders.DONE]:
        if regex.match(folder):
            return folder
    # Want arg='d' to match keyword DUE instead of DONE
    if regex.match(folders.DONE) and len(arg) > 1:
        return folders.DONE
    return None


def parse_keyword(arg):
    max_date = datetime.date(9999, 12, 31)
    if arg.lower() in ['d', 'du', 'due']:
        return 'due', max_date
    match = re.fullmatch(r'(due|du|d)\+(\d+)(d|w|m|y)', arg.lower())
    if match:
        shifted_date = datetime.date.today()
        n = int(match.group(2))
        dateunit = match.group(3)
        if dateunit == 'd':
            shifted_date = shifted_date + relativedelta(days=n)
        elif dateunit == 'w':
            shifted_date += relativedelta(weeks=n)
        elif dateunit == 'm':
            shifted_date += relativedelta(months=n)
        elif dateunit == 'y':
            shifted_date += relativedelta(years=n)
        return 'due', shifted_date

    if arg.lower() in ['r', 're', 'rem', 'remi', 'remind']:
        return 'remind', max_date
    match = re.fullmatch(r'(remind|remin|remi|rem|re|r)\+(\d+)(d|w|m|y)',
                         arg.lower())
    if match:
        shifted_date = datetime.date.today()
        n = int(match.group(2))
        dateunit = match.group(3)
        if dateunit == 'd':
            shifted_date = shifted_date + relativedelta(days=n)
        elif dateunit == 'w':
            shifted_date += relativedelta(weeks=n)
        elif dateunit == 'm':
            shifted_date += relativedelta(months=n)
        elif dateunit == 'y':
            shifted_date += relativedelta(years=n)
        return 'remind', shifted_date

    return None, None
