import sys

from todone.parser.commands import done
from todone.parser.commands import folder
from todone.parser.commands import help as help_
from todone.parser.commands import list as list_
from todone.parser.commands import move
from todone.parser.commands import new
from todone.parser.commands import setup
from todone.parser.commands import version

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
             {'name': 'command', 'options': _ALLOWED_COMMANDS}),
            (factory.PresetArgument.all_remaining_passthrough,
             {'name': 'args'}),
        ]
        self.parser = factory.ParserFactory.from_arg_list(parser_initialization)

    @property
    def commands(self):
        self._commands = []
        try:
            self.parser.parse(self.args)
            self._build_config_command()
            self._build_parsed_command()
            return self._commands
        except pe.ArgumentError:
            return [('error', {'message': 'Invalid argument(s)'}),
                    ('help', {'short': True})]

    def _build_config_command(self):
        cmd = ('configure', {'file': self.parser.parsed_data['config']})
        self._commands.append(cmd)

    def _build_parsed_command(self):
        arg_parser = ArgParser(self.parser.parsed_data['command'],
                               self.parser.parsed_data['args'])
        self._commands = self._commands + arg_parser.commands


class ArgParser:
    def __init__(self, command, args):
        self.parser = self._parser_init(command)
        self._args = args
        self._command = command

    @property
    def commands(self):
        try:
            return [(self._command, self.parser(self._args))]
        except pe.ArgumentError as e:
            return [('error',
                     {'message': 'Invalid argument(s) for {} command. {}'
                      .format(self._command, e)}),
                    ('help', {'short': True, 'subcommand': self._command})]

    def _parser_init(self, command):
        init = {
            'help': help_.parse_args,
            'folder': folder.parse_args,
            'list': list_.parse_args,
            'move': move.parse_args,
            'new': new.parse_args,
            'setup': setup.parse_args,
            'done': done.parse_args,
            'version': version.parse_args,
        }
        return init[command]

_ALLOWED_COMMANDS = {
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
