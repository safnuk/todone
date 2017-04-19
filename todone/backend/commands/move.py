"""Module for the move command, which moves a todo to a different
folder or project.
"""
from todone import backend
import todone.backend.utils as utils


def move_todo(args):
    """Move a todo from most recent search to a new folder or project.

    usage: todone move N folder/
           todone move N [project]

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    todos = backend.SavedList.get_todos_from_most_recent_search()
    target = todos[args['index']-1]
    if args['folder']:
        target.folder = utils.match_folder(args['folder'])
        print('Moved: {} -> {}/'.format(target.action, target.folder.name))
    elif args['parent']:
        target.parent = utils.match_parent(**args['parent'])
        print('Moved: {} -> [{}]'.format(target.action, target.parent.action))
    target.save()

move_todo.short_help = """
usage: todone move N folder/
       todone move N [project]
where N is the number of the todo referenced in most recent search.
"""
