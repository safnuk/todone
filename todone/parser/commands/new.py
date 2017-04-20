"""Module for the new command, which creates a new todo."""
from todone.parser import factory


def parse_args(args=[]):
    parser_initialization = [
        (factory.PresetArgument.parent,
         {'name': 'parent',
          'positional': False}),
        (factory.PresetArgument.folder,
         {'name': 'folder'}),
        (factory.PresetArgument.due_date,
         {'name': 'due'}),
        (factory.PresetArgument.remind_date,
         {'name': 'remind'}),
        (factory.PresetArgument.all_remaining,
         {'name': 'action'}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
