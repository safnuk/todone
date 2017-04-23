"""Entry point to the todone command-line interface."""
from todone.backend import dispatch
from todone.parser import parser
from todone import printer
from todone import response as resp

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(args=None):
    arg_parser = parser.Parser(args)
    responses = []
    for command, args in arg_parser.commands:
        response = dispatch.dispatch_command(command, args)
        if type(response) == resp.Response:
            responses.append(response)
        if type(response) == list:
            responses += response
    for response in responses:
        printer.output(response)
