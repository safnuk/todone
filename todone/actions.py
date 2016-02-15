from todone.todos import folders
from todone.todos.db import Todo

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'
HELP_TEXT = ('usage: todone [--version] [--help] <command> [<args>]')

def help_text(args):
    print(SCRIPT_DESCRIPTION)


def list_items(args):
    pass

def dispatch_action(action, args):
    CHOICES[action](args)


CHOICES = {
    'help': help_text,
    'list': list_items,
}
