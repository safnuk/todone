from todone import exceptions


class Response:
    ERROR = 'error'
    NOOP = 'noop'
    SUCCESS = 'success'
    TODO_QUERY = 'todo_query'
    FOLDER_QUERY = 'folder_query'

    valid_statuses = [ERROR, SUCCESS, TODO_QUERY, FOLDER_QUERY, NOOP]

    def __init__(self, status, response):
        if status not in self.valid_statuses:
            raise exceptions.ArgumentError("Invalid status '{}' specified"
                                           .format(status))
        self.status = status
        self.response = response

    def __iter__(self):
        yield self.status
        yield self.response
        return

    def __getitem__(self, index):
        if index == 0:
            return self.status
        if index == 1:
            return self.response
        raise KeyError("Index out of range")

    def __str__(self):
        return '({}, {})'.format(self.status, self.response)

    def __repr__(self):
        return 'Response{}'.format(self)
