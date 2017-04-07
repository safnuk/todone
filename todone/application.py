from todone.commands import dispatch

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'


def main(args=None):
    dispatcher = dispatch.CommandDispatcher(args)
    dispatcher.parse_args()
    dispatcher.configure()
    dispatcher.dispatch_command()
