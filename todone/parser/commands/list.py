"""Module for searching the database based on user-supplied queries, and
display the result to the user.
"""
from todone.parser import factory


def parse_args(args=[]):
    parser_initialization = [
        (factory.PresetArgument.file,
         {'name': 'file'}),
        (factory.PresetArgument.parent,
         {'name': 'parent'}),
        (factory.PresetArgument.folder,
         {'name': 'folder'}),
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
