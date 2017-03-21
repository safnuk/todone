ERROR = "Class {} doesn't implement {}"


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
