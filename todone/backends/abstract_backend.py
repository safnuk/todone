ERROR = "Class {} doesn't implement {}"

DEFAULT_FOLDERS = {
    'inbox': 'inbox',  # default location for new todos
    # initial folders created
    'folders': [
        'today', 'next', 'inbox', 'cal',
        'done', 'someday', 'garbage'
    ],
    'active': ['today', 'next', 'inbox'],  # folders searched if none specified
    'inactive': ['done', 'garbage'],  # never searched unless specified
    'cal': ['cal'],  # behavior not yet defined (future plans)
    # current: includes upcoming reminders and due todos from other folders
    # when searching for today/ (behavior may change in future)
    'today': ['today'],
    'trash': ['garbage'],  # folder that is regularly cleared
}


class AbstractFolder:
    @classmethod
    def new(cls, folder_name):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "new()"))

    @classmethod
    def rename(cls, old_folder_name, new_folder_name):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "rename()"))

    @classmethod
    def remove(cls, folder_name):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "remove()"))

    @classmethod
    def all(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "all()"))


class AbstractTodo:
    @classmethod
    def query(cls, **search_parameters):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "query()"))

    @classmethod
    def active_todos(cls):
        """Construct a select query of all active todos. """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "active_todos()"))

    @classmethod
    def get_projects(cls, search_string):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_projects()"))

    @classmethod
    def new(cls, **args):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "new()"))

    def save(self):
        raise NotImplementedError(
            ERROR.format(self.__class__.__name__, "save()"))


class AbstractSavedList:
    @classmethod
    def get_most_recent(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_most_recent()"))

    @classmethod
    def get_todos_in_list(cls, listname):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_todos_in_list()"))

    @classmethod
    def get_todos_from_most_recent_search(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__,
                         "get_todos_from_most_recent_search()"))

    @classmethod
    def save_search(cls, name, todo_query):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "save_search()"))

    @classmethod
    def save_most_recent_search(cls, todo_query):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "save_most_recent_search()"))


class AbstractDatabase:
    @classmethod
    def create(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "create()"))

    @classmethod
    def connect(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "connect()"))

    @classmethod
    def close(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "close()"))

    @classmethod
    def update(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "update()"))
