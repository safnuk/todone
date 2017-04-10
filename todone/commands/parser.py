import sys

from todone.parser import factory
from todone.parser import exceptions as pe


class Parser:
    DEFAULT_ARGS = ['help', ]

    def __init__(self, args):
        self._store_args(args)
        self._setup_parser()

    def _store_args(self, args):
        if args:
            self.args = args
        else:
            self.args = (sys.argv[1:]
                         if len(sys.argv) > 1
                         else self.DEFAULT_ARGS)

    def _setup_parser(self):
        parser_initialization = [
            (factory.PresetArgument.config, {'name': 'config'}),
            (factory.PresetArgument.required_switch,
             {'name': 'command', 'options': ALLOWED_COMMANDS}),
            (factory.PresetArgument.all_remaining_passthrough,
             {'name': 'args'}),
        ]
        self.parser = factory.ParserFactory.from_arg_list(parser_initialization)

    @property
    def commands(self):
        try:
            self.parser.parse(self.args)
        except pe.ArgumentError:
            return [{'command': 'error', 'message': 'Invalid argument(s)'}]


ALLOWED_COMMANDS = {
    '-h',
    '--help',
    'help',
    '-v',
    '--version',
    'version',
    'folder',
    'list',
    'move',
    'new',
    'setup',
    'done',
}
