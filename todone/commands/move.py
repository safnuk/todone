"""Module for the move command, which moves a todo to a different
folder or project.
"""
from todone import backend
from todone.commands import utils
from todone.parser import factory


def move_todo(args):
    """Move a todo from most recent search to a new folder or project.

    usage: todone move N folder/
           todone move N [project]

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    parsed_args = parse_args(args)
    todos = backend.SavedList.get_todos_from_most_recent_search()
    target = todos[parsed_args['index']-1]
    if parsed_args['folder']:
        target.folder = utils.match_folder(parsed_args['folder'])
        print('Moved: {} -> {}/'.format(target.action, target.folder.name))
    elif parsed_args['parent']:
        target.parent = utils.match_parent(**parsed_args['parent'])
        print('Moved: {} -> [{}]'.format(target.action, target.parent.action))
    target.save()

move_todo.short_help = """
usage: todone move N folder/
       todone move N [project]
where N is the number of the todo referenced in most recent search.
"""


def parse_args(args):
    parser_initialization = [
        (factory.PresetArgument.index,
         {'name': 'index'}),
        (factory.PresetArgument.parent,
         {'name': 'parent'}),
        (factory.PresetArgument.folder,
         {'name': 'folder'}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
