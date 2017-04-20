"""Module for displaying help messages for todone commands."""

import todone.backend.dispatch as dispatch
from todone.parser import factory


def parse_args(args):
    parser_initialization = [
        (factory.PresetArgument.optional_switch,
         {'name': 'short',
          'options': ['-s', '--short'],
          'positional': False}),
        (factory.PresetArgument.optional_switch,
         {'name': 'subcommand',
          'options': dispatch.COMMAND_MAPPING}),
    ]
    parser = factory.ParserFactory.from_arg_list(parser_initialization)
    parser.parse(args)
    return parser.parsed_data
