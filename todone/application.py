"""Entry point to the todone command-line interface."""
from todone.backend import dispatch
from todone.parser import parser

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(args=None):
    arg_parser = parser.Parser(args)
    responses = []
    print("Commands:")
    for command, args in arg_parser.commands:
        print('{}: {}'.format(command, args))
        response = dispatch.dispatch_command(command, args)
        if response:
            responses.append(response)
