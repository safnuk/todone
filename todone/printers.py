def print_todo(n, todo):
    print('{} {}'.format(n, todo))


def print_todo_list(query):
    current_project = None
    for (n, todo) in enumerate(query, 1):
        if todo.parent != current_project:
            print_project_header(todo.parent)
            current_project = todo.parent
        print_todo(n, todo)


def print_project_header(project):
    print('[{}]'.format(project.action))
