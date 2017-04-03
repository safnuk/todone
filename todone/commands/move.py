from todone.backend import Folder, SavedList
from todone.parser.factory import ParserFactory, PresetArgument


def move_todo(args):
    """Move a todo from most recent search to a new folder or project.

    usage: todone move N folder/
           todone move N [project]

    """
    parsed_args = parse_args(args)
    todos = SavedList.get_todos_from_most_recent_search()
    target = todos[parsed_args['index']-1]
    if parsed_args['folder']:
        target.folder = parsed_args['folder']
        print('Moved: {} -> {}/'.format(target.action, target.folder.name))
    elif parsed_args['parent']:
        target.parent = parsed_args['parent']
        print('Moved: {} -> [{}]'.format(target.action, target.parent.action))
    target.save()

move_todo.short_help = """
usage: todone move N folder/
       todone move N [project]
where N is the number of the todo referenced in most recent search.
"""


def parse_args(args):
    parser_initialization = [
        (PresetArgument.index,
         {'name': 'index'}),
        (PresetArgument.unique_project,
         {'name': 'parent'}),
        (PresetArgument.folder,
         {'name': 'folder',
          'options': [f.name for f in Folder.all()]}),
    ]
    parser = ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
