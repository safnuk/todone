import argparse
import os
import sys

from todone.commands import COMMAND_MAPPING, dispatch

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'

def main(cli_args=None):
    if cli_args is None:
        cli_args = sys.argv[1:] if len(sys.argv) > 1 else ['help']

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('command', choices=COMMAND_MAPPING)
    parser.add_argument('args', nargs='*')
    parsed_args = parser.parse_args(cli_args)

    dispatch(parsed_args.command, parsed_args.args)
