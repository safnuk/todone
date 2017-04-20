"""Module for creating a configuration file (if necessary) and initializing
the database.
"""
from todone.backend.commands import Setup
from todone.parser import factory


def parse_args(args=[]):
    argtypes = [
        (factory.PresetArgument.required_switch,
         {'name': 'subcommand', 'options': Setup.COMMANDS}),
    ]
    parser = factory.ParserFactory.from_arg_list(argtypes)
    parser.parse(args)
    return parser.parsed_data
