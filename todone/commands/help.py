import textwrap

import todone

def help_text(args):
    """
    Command-line agenda and todo-list manager.

    usage: todone [--version] [--help] <command> [<args>]

    Allowed commands include:
        help    Display this help message
        list    Print a list of todos matching given search terms

    See todone help <command> to read more about a specific command.
    """
    if not args:
        print(textwrap.dedent(help_text.__doc__))
    if len(args) == 1 and args[0].lower() in todone.commands.COMMAND_MAPPING:
        print(textwrap.dedent(todone.commands.COMMAND_MAPPING[args[0].lower()].__doc__))
