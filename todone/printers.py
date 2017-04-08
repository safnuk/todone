"""Basic console output module.

Used to output a formatted list of todos to the screen.
"""


def print_todo_list(query):
    """Print the given list of todos to the screen.

    :param query: Iterable set of todo items

    """
    current_project = None
    for (n, todo) in enumerate(query, 1):
        if todo.parent != current_project:
            _print_project_header(todo.parent)
            current_project = todo.parent
        _print_todo(n, todo)


def _print_todo(n, todo):
    print('{} {}'.format(n, todo))


def _print_project_header(project):
    print('[{}]'.format(project.action))
