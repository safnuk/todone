"""Module for command which moves a todo to the ``done/`` folder."""
from todone.commands import move
from todone.parser import factory


def done_todo(args):
    """Move a todo from most recent search to the done folder.

    usage: todone done N

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    parsed_args = parse_args(args)
    move.move_todo([str(parsed_args['index']), 'done/'])

done_todo.short_help = """
usage: todone done N

where N is the number of the todo referenced in most recent search.
"""


def parse_args(args):
    parser_initialization = [
        (factory.PresetArgument.index,
         {'name': 'index'}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
