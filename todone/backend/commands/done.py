"""Module for command which moves a todo to the ``done/`` folder."""
from todone.backend.commands import move


def done_todo(args):
    """Move a todo from most recent search to the done folder.

    usage: todone done N

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    move.move_todo([str(args['index']), 'done/'])

done_todo.short_help = """
usage: todone done N

where N is the number of the todo referenced in most recent search.
"""
