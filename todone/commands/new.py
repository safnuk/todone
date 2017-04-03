from todone.backend import DEFAULT_FOLDERS, Folder, Todo
from todone.parser.factory import ParserFactory, PresetArgument


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
    Todo.new(**parsed_args)
    msg = 'Added: {}/{}'.format(parsed_args['folder'], parsed_args['action'])
    if parsed_args['parent']:
        msg += ' [{}]'.format(parsed_args['parent'].action)
    print(msg)

new_todo.short_help = """
usage: todone new [folder/] [tags and todo string]
"""


def parse_args(args=[]):
    parser_initialization = [
        (PresetArgument.unique_project,
         {'name': 'parent',
          'positional': False}),
        (PresetArgument.folder,
         {'name': 'folder',
          'options': [f.name for f in Folder.all()],
          'format_function': _default_inbox}),
        (PresetArgument.due_date,
         {'name': 'due'}),
        (PresetArgument.remind_date,
         {'name': 'remind'}),
        (PresetArgument.all_remaining,
         {'name': 'action'}),
    ]
    parser = ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data


def _default_inbox(x):
    if x:
        return x[0]
    return DEFAULT_FOLDERS['inbox']
