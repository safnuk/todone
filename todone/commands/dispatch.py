"""Dispatch a list of args to a specified command."""

import sys

from todone import backend, config
from todone.commands import done
from todone.commands import folder
from todone.commands import help as cmd_help
from todone.commands import list as cmd_list
from todone.commands import move
from todone.commands import new
from todone.commands import setup
from todone.parser import factory
from todone.parser import exceptions as pe

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
            (factory.PresetArgument.config, {'name': 'config'}),
            (factory.PresetArgument.required_switch,
             {'name': 'command', 'options': COMMAND_MAPPING}),
            (factory.PresetArgument.all_remaining_passthrough,
             {'name': 'args'}),
        ]
        self.parser = factory.ParserFactory.from_arg_list(parser_initialization)

    def parse_args(self):
        """Parse :attr:`args` for the pattern ``[command, *remaining_args]``.

        :raises SystemExit: if a valid command cannot be parsed
        from :attr:`args`
        """
        try:
            self.parser.parse(self.args)
        except pe.ArgumentError:
            print('Invalid argument(s)')
            dispatch_command('help', ['--short'])
            raise SystemExit(1)

    def configure(self):
        """Setup program-wide configuration settings.

        Uses either the configuration filename parsed from :attr:`args`,
        or, if missing, the default config behavior of :mod:`config`.

        Must be called *after* calling :meth:`parse_args`.
        """
        config.configure(self.parser.parsed_data['config'])

    def dispatch_command(self):
        """Call command determined from parsed arguments.

        Must be called *after* calling :meth:`parse_args` and
        :meth:`configure`.
        """
        try:
            backend.Database.connect()
            dispatch_command(
                self.parser.parsed_data['command'],
                self.parser.parsed_data['args']
            )
            backend.Database.close()
        except backend.DatabaseError as e:
            print(DB_HELP_MSG.format(e))
            pass


def dispatch_command(action, args):
    try:
        COMMAND_MAPPING[action](args)
    except pe.ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            action, e))
        COMMAND_MAPPING['help'](['--short', action])

COMMAND_MAPPING = {
    '-h': cmd_help.help_text,
    '--help': cmd_help.help_text,
    'help': cmd_help.help_text,
    '-v': setup.version,
    '--version': setup.version,
    'version': setup.version,
    'folder': folder.folder_command,
    'list': cmd_list.list_items,
    'move': move.move_todo,
    'new': new.new_todo,
    'setup': setup.setup_db,
    'done': done.done_todo,
}
