"""Basic console output.

Used to output response messages to the screen.
"""
from todone import response as resp


def output(response):
    if response.status == resp.Response.NOOP:
        return
    elif response.status == resp.Response.SUCCESS:
        print(response)
    elif response.status == resp.Response.ERROR:
        print(response)
    elif response.status == resp.Response.FOLDER_QUERY:
        for folder in response.response:
            print(folder)
    elif response.status == resp.Response.TODO_QUERY:
        print_todo_list(response.response)
    else:
        raise NotImplementedError('Cannot print response status {}'
                                  .format(response.status))


def print_todo_list(query):
    """Print the given list of todos to the screen.

    :param query: Iterable set of todo item groups

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
