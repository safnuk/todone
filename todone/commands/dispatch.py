"""Dispatch a list of args to a specified command."""

import sys

from todone.backend import Database, DatabaseError
from todone.commands.done import done_todo
from todone.commands.folder import folder_command
from todone.commands.help import help_text
from todone.commands.list import list_items
from todone.commands.move import move_todo
from todone.commands.new import new_todo
from todone.commands.setup import setup_db, version
from todone.config import configure
from todone.parser.factory import ParserFactory, PresetArgument
from todone.parser.textparser import ArgumentError

DB_HELP_MSG = """{}

Make sure you have a valid configuration file:
    > todone help configure
then enter
    > todone setup init
to initialize the database before using.
"""


class CommandDispatcher:
    """Dispatch a list of arguments to a specified command.

    Split off the first keyword in :attr:`args` and use it to determine
    which command to call. The remaining elements of :attr:`args` are
    passed along to the command unchanged.

    If :attr:`args` is empty or :obj:`None`,
    use arguments passed from the command line. If both are empty,
    initialize as if calling the :func:`~commands.help_text` command.

    :param args: list of strings to be parsed
    """
    DEFAULT_ARGS = ['help', ]

    def __init__(self, args):
        """Initialize CommandDispatcher.
        """
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
            (PresetArgument.config, {'name': 'config'}),
            (PresetArgument.required_switch,
             {'name': 'command', 'options': COMMAND_MAPPING}),
            (PresetArgument.all_remaining_passthrough, {'name': 'args'}),
        ]
        self.parser = ParserFactory.from_arg_list(parser_initialization)

    def parse_args(self):
        """Parse :attr:`args` for the pattern ``[command, *remaining_args]``.

        :raises SystemExit: if a valid command cannot be parsed
        from :attr:`args`
        """
        try:
            self.parser.parse(self.args)
        except ArgumentError:
            print('Invalid argument(s)')
            dispatch_command('help', ['--short'])
            raise SystemExit(1)

    def configure(self):
        """Setup program-wide configuration settings.

        Uses either the configuration filename parsed from :attr:`args`,
        or, if missing, the default config behavior of :mod:`config`.

        Must be called *after* calling :meth:`parse_args`.
        """
        configure(self.parser.parsed_data['config'])

    def dispatch_command(self):
        """Call command determined from parsed arguments.

        Must be called *after* calling :meth:`parse_args` and
        :meth:`configure`.
        """
        try:
            Database.connect()
            dispatch_command(
                self.parser.parsed_data['command'],
                self.parser.parsed_data['args']
            )
            Database.close()
        except DatabaseError as e:
            print(DB_HELP_MSG.format(e))
            pass


def dispatch_command(action, args):
    try:
        COMMAND_MAPPING[action](args)
    except ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            action, e))
        COMMAND_MAPPING['help'](['--short', action])

COMMAND_MAPPING = {
    '-h': help_text,
    '--help': help_text,
    'help': help_text,
    '-v': version,
    '--version': version,
    'version': version,
    'folder': folder_command,
    'list': list_items,
    'move': move_todo,
    'new': new_todo,
    'setup': setup_db,
    'done': done_todo,
}
