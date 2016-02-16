from todone.backends import folders
from todone.backends.db import Todo
from todone.printers import print_todo

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'
HELP_TEXT = ('usage: todone [--version] [--help] <command> [<args>]')

def help_text(args):
    print(SCRIPT_DESCRIPTION)


def list_items(args):
    if not args:
        for todo in Todo.select().where(Todo.folder == folders.TODAY):
            print_todo(todo)
        return
    if len(args) > 0 and args[0].upper() in folders.FOLDERS:
        for todo in Todo.select().where(Todo.folder == args[0].upper()):
            print_todo(todo)
    else:
        assert 0


def dispatch(action, args):
    CHOICES[action](args)


CHOICES = {
    'help': help_text,
    'list': list_items,
}
