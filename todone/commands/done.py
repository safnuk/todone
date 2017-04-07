"""Module for command which moves a todo to the ``done/`` folder."""
from todone.commands.move import move_todo
from todone.parser.factory import ParserFactory, PresetArgument


def done_todo(args):
    """Move a todo from most recent search to the done folder.

    usage: todone done N

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    parsed_args = parse_args(args)
    move_todo([str(parsed_args['index']), 'done/'])

done_todo.short_help = """
usage: todone done N

where N is the number of the todo referenced in most recent search.
"""


def parse_args(args):
    parser_initialization = [
        (PresetArgument.index,
         {'name': 'index'}),
    ]
    parser = ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
