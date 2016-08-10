from todone.backends.db import Folder, Todo
from todone.commands.constants import DUE_REGEX, REMIND_REGEX
from todone import config
from todone.parser.format import (
    ApplyFunctionFormat,
    DateFormat,
)
from todone.parser.match import (
    AlwaysMatch,
    FolderMatch,
    ProjectMatch,
    RegexMatch,
)
from todone.parser.textparser import TextParser


def new_todo(args):
    """Create one or more todo items or projects.

    usage: todone new [folder/] [tags and todo string]

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
    Todo.create(**parsed_args)
    print('Added: {} to {}'.format(
        parsed_args['action'], parsed_args['folder']))

new_todo.short_help = """
usage: todone new [folder/] [tags and todo string]
"""


def parse_args(args=[]):
    parser = TextParser()
    parser.add_argument(
        'parent', match=ProjectMatch,
        nargs='?',
        positional=False,
        format_function=_get_project_todo,
        format=ApplyFunctionFormat
    )
    parser.add_argument(
        'folder',
        options=[f.name for f in Folder.select()],
        match=FolderMatch, nargs='?',
        format=ApplyFunctionFormat,
        format_function=_default_inbox
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
        'action', match=AlwaysMatch,
        nargs='*',
        format=ApplyFunctionFormat,
        format_function=' '.join
    )
    parser.parse(args)
    return parser.parsed_data


def _default_inbox(x):
    if x:
        return x[0]
    return config.settings['folders']['default_inbox']


def _get_project_todo(x):
    if x:
        return Todo.get_projects(x[0])[0]
    return None
