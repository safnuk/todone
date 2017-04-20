"""Module for the move command, which moves a todo to a different
folder or project.
"""
from todone.parser import factory


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
