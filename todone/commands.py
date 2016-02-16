from todone.backends import folders
from todone.backends.db import Todo
from todone.printers import print_todo

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'

def help_text(args):
    """Command-line agenda and todo-list manager.

usage: todone [--version] [--help] <command> [<args>]

Allowed commands include:
    help    Display this help message
    list    Print a list of todos matching given search terms

See todone help <command> to read more about a specific command.
    """
    if not args:
        print(help_text.__doc__)
    if len(args) == 1 and args[0].lower() in CHOICES:
        print(CHOICES[args[0].lower()].__doc__)


def list_items(args):
    """
    Print a list of todos matching given search terms.

    Usage: todone list [.file] [keyword(s)] [regular expression]

    Search criteria can be any string expression. Special keywords
    are: today, next, inbox, remind[+#{d,w,m,y}], due[+#{d,w,m,y}],
    all, done (shortened versions accepted when unambiguous).

    Apart from special keywords, the remainder of the search string
    is interprested as a python regular expression. However, searches
    are always case insensitive.

    today, t:   restricts to today todos
    next, n:    restricts to next todos
    inbox, i:   restricts to inbox todos
    remind, r:  restricts to reminder todos
    r[emind]+N{d|w|m|y}:
                restricts to reminders with dates within the
                specified interval (N an integer)
    due, d:     restricts to todos with a due date
    d[ue]+N{d|w|m|y}: 
                restricts to todos due within specified interval
    all, a:     every active todo matches the search criteria (done and
                someday todos are excluded).
    done:       restricts to done todos
    someday:    restricts to someday todos

    If .file is specified, then search results are saved to .file.
    Otherwise, the default file is .todos.

    If no search criteria is provided, the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently used search is used.

    E.g.,
        > todone list .my_search today @Work
            (Lists all today items containing tag @Work)
        > todone list next due+1w [My Project]
            (Lists all next items from project [My Project] due in
             the next week)
        > todone list
            (Repeats most recent search)
        > todone list .my_search
            (Repeats list from first search)
        > todone list
            (Repeats list from first search)
    """
    # TODO: Decide when to clear canceled/done items from saved lists
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
