from todone.backends import folders
from todone.backends.db import Todo
from todone.printers import print_todo

SCRIPT_DESCRIPTION = 'Command-line agenda and todo-list manager.'
HELP_TEXT = ('usage: todone [--version] [--help] <command> [<args>]')

def help_text(args):
    print(SCRIPT_DESCRIPTION)


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

    today, t: restricts to todos with today prefix
    next, n: restricts to todos with next prefix
    inbox, i: restricts to todos with inbox prefix
    remind, r: restricts to todos with reminder prefix
    r[emind]+#{d,w,m,y}: restricts to reminders with dates within the
        specified interval.
    due, d: restricts to todos with a due date
    d[ue]+#{d,w,m,y}: restricts to todos due within specified interval
    all, a: every active todo matches the search criteria (done and
        someday todos are excluded).
    done: restricts to todos with done prefix.
    someday: restricts to todos with someday prefix.

    If .file is specified, then search results are saved to .file.
    Otherwise, the default file is .todos.

    If no search criteria is provided, the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently used search is used.

    E.g.,
        > todone list .my_search today @Work
            (Lists all today items containing tag @Work)
        > todone list next [My Project]
            (Lists all next items from project [My Project])
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
