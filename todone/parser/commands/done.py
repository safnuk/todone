"""Module for command which moves a todo to the ``done/`` folder."""
from todone.parser import factory


def parse_args(args):
    parser_initialization = [
        (factory.PresetArgument.index,
         {'name': 'index'}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
