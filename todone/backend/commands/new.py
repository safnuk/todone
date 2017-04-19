"""Module for the new command, which creates a new todo."""
from todone import backend
import todone.backend.utils as utils


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
    if args['folder']:
        args['folder'] = utils.match_folder(args['folder'])
    else:
        args['folder'] = backend.DEFAULT_FOLDERS['inbox']
    if args['parent']:
        args['parent'] = utils.match_parent(
            **args['parent'])
    backend.Todo.new(**args)
    msg = 'Added: {}/{}'.format(args['folder'], args['action'])
    if args['parent']:
        msg += ' [{}]'.format(args['parent'].action)
    print(msg)

new_todo.short_help = """
usage: todone new [folder/] [tags and todo string]
"""
