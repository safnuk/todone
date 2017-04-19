"""Module for the new command, which creates a new todo."""
from todone import backend
from todone.commands import utils
from todone.parser import factory


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
    if parsed_args['folder']:
        parsed_args['folder'] = utils.match_folder(parsed_args['folder'])
    else:
        parsed_args['folder'] = backend.DEFAULT_FOLDERS['inbox']
    if parsed_args['parent']:
        parsed_args['parent'] = utils.match_parent(
            **parsed_args['parent'])
    backend.Todo.new(**parsed_args)
    msg = 'Added: {}/{}'.format(parsed_args['folder'], parsed_args['action'])
    if parsed_args['parent']:
        msg += ' [{}]'.format(parsed_args['parent'].action)
    print(msg)

new_todo.short_help = """
usage: todone new [folder/] [tags and todo string]
"""


def parse_args(args=[]):
    parser_initialization = [
        (factory.PresetArgument.parent,
         {'name': 'parent',
          'positional': False}),
        (factory.PresetArgument.folder,
         {'name': 'folder'}),
        (factory.PresetArgument.due_date,
         {'name': 'due'}),
        (factory.PresetArgument.remind_date,
         {'name': 'remind'}),
        (factory.PresetArgument.all_remaining,
         {'name': 'action'}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
