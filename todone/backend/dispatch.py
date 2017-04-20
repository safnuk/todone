"""Dispatch a list of args to a specified command."""

from todone.backend import commands as cmd
from todone.parser import exceptions as pe


def dispatch_command(command, args):
    try:
        return COMMAND_MAPPING[command].run(args)
    except pe.ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            command, e))
        return COMMAND_MAPPING['help'].run({'short': '--short',
                                            'subcommand': command})

COMMAND_MAPPING = {
    '-h': cmd.Help,
    '--help': cmd.Help,
    'help': cmd.Help,
    '-v': cmd.Version,
    '--version': cmd.Version,
    'version': cmd.Version,
    'folder': cmd.Folder,
    'list': cmd.List,
    'move': cmd.Move,
    'new': cmd.New,
    'setup': cmd.Setup,
    'done': cmd.Done,
    'configure': cmd.Configure,
}
