from datetime import date
from dateutil.relativedelta import relativedelta
import re

from todone.backends import folders
from todone.backends.db import Todo


def new_todo(args):
    """Create one or more todo items or projects.

    Usage: todone new [folder] [tags and todo string]

    Create new todo the given title.

    Allowed folder names are:
        inbox, next, today, project, cal, someday
    Partial matches are also allowed. The todo is created in the
    given folder, if provided, otherwise it defaults to INBOX.

    The todo title can be any text string, but should be unique.

    Allowed tags are:

    due[+N{d|w|m|y} | YYYY-MM-DD]
    remind[+N{d|w|m|y} | YYYY-MM-DD][+N{d|w|m|y}]
    [Project name]
    [Project number]
    [query]

    Project number is the unique number id associated to a project,
    obtained from, e.g. "todone list project". If "[query]"
    (or any partial match, such as "[q]") appears, then the user is
    presented with a list of current projects to input. If a
    project is entered that does not exist, a new one is created
    at the same time as the todo.
    If keywords due or remind appear without a date, the user is prompted
    to enter a date. Notation remind+N{d|w|m|y}+N{d|w|m|y} sets up a
    recurring reminder. e.g.
        r+7d+1m
    sets up a reminder for 7 days from now, with a new reminder created
    1 month after completion (ad nauseum).

    The title used for the todo consists of the argument string remaining
    after removing all valid tags. It should be unique for the specified
    project.
    """
    parsed_args = parse_args(args)
    Todo.create(
        action=parsed_args['todo'],
        folder=parsed_args['folder'],
        due_date=parsed_args['due'],
    )
    print('Added: {} to {}'.format(
        parsed_args['todo'], parsed_args['folder']))


def parse_args(args=[]):
    parsed = {
        'folder': folders.INBOX,
        'todo': [],
        'due': None,
    }
    folder = parse_folder(args[0])
    if folder:
        parsed['folder'] = folder
        args = args[1:]
    for arg in args:
        key, value = parse_keyword(arg)
        if key:
            parsed[key] = value
        else:
            parsed['todo'].append(arg)
    parsed['todo'] = ' '.join(parsed['todo'])
    return parsed


def parse_folder(arg):
    if not arg:
        return None
    regex = re.compile('^' + arg, re.IGNORECASE)
    for folder in [folders.INBOX, folders.NEXT, folders.TODAY,
                   folders.PROJECT, folders.CAL, folders.SOMEDAY]:
        if regex.match(folder):
            return folder
    return None


def parse_keyword(arg):
    match = re.fullmatch(r'(due|du|d)\+(\d+)(d|w|m|y)', arg.lower())
    if match:
        shifted_date = date.today()
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
    return None, None
