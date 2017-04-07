"""Module for searching the database based on user-supplied queries, and
display the result to the user.
"""
from todone import backend, printers
from todone.parser import factory


def list_items(args):
    """
    Print a list of todos matching given search terms.

    usage: todone list [.file] [folder/] [tags and keywords]

    Search criteria can be any string expression.

    Allowed folder keywords are any valid folder name, followed by
    a slash. Examples: today/, next/, inbox/, someday/, done/. Shortened
    versions accepted when unambiguous, so, for example "done/", "don/",
    "do/", and "d/" all indicate the done folder.

    If folder is not specified, the search is over all active
    folders (default is: inbox/, next/, today/).

    If folder is today/, then, in addition to items in the today
    folder, items with a reminder or due date prior to or equal to
    today's date are also included. This behavior may change in future
    versions.

    Allowed tags are:

    due[+N{d|w|m|y}],
    remind[+N{d|w|m|y}],
    [project name]

    The remainder of the search string provides keywords that must
    appear in the todo title. However, searches are always case
    insensitive.

    If .file is specified, then search results are saved to .file.

    If no search criteria is provided, then the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently run search is listed.

    E.g.,
        > todone list .my_search today/ @Work
            Lists all today items containing tag @Work, and saves to .my_search
        > todone list n/due+1w [My Project]
            Lists all next items from project [My Project] due in
            the next week
        > todone list
            Repeats most recent search
        > todone list .my_search
            Repeats list from first search
        > todone list
            Repeats list from first search
    """
    parsed_args = parse_args(args)
    if is_loading_saved_search(parsed_args):
        query = backend.SavedList.get_todos_in_list(parsed_args['file'])
    else:
        query = backend.Todo.query(**parsed_args)
        backend.SavedList.save_search(parsed_args['file'], query)
    backend.SavedList.save_most_recent_search(query)
    printers.print_todo_list(query)

list_items.short_help = """
usage: todone list [.file] [folder/] [tags and keywords]
"""


def is_loading_saved_search(args):
    for key, value in args.items():
        if (key != 'file') and value:
            return False
    return True


def parse_args(args=[]):
    parser_initialization = [
        (factory.PresetArgument.file,
         {'name': 'file'}),
        (factory.PresetArgument.all_matching_projects,
         {'name': 'parent'}),
        (factory.PresetArgument.folder,
         {'name': 'folder',
          'options': [x.name.lower() for x in backend.Folder.all()]}),
        (factory.PresetArgument.due_date,
         {'name': 'due'}),
        (factory.PresetArgument.remind_date,
         {'name': 'remind'}),
        (factory.PresetArgument.all_remaining,
         {'name': 'keywords',
          'format_function': lambda x: x}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
