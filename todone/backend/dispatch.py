"""Dispatch a list of args to a specified command."""

from todone.backend import commands as cmd
from todone.parser import exceptions as pe


def dispatch_command(command, args):
    try:
        return cmd.COMMAND_MAPPING[command].run(args)
    except pe.ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            command, e))
        return cmd.COMMAND_MAPPING['help'].run({'short': '--short',
                                                'subcommand': command})
