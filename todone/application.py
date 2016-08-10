
from todone.commands.dispatch import CommandDispatcher

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(args=None):
    dispatcher = CommandDispatcher(args)
    dispatcher.parse_args()
    dispatcher.configure()
    dispatcher.dispatch_command()
