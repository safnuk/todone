"""Determine which backend to use based on global configuration settings,
allowing the rest of the program to simply utilize :class:`backend.Todo`,
:class:`backend.Folder`, etc., without knowing which backend is in use.
"""
from todone import backend
from todone import config
from todone.backend import abstract_backend as abstract

SQL_TYPES = ['sqlite3', 'postgresql']


class Folder(abstract.AbstractFolder):
    @classmethod
    def new(cls, folder_name):
        return get_module().Folder.new(folder_name)

    @classmethod
    def rename(cls, old_folder_name, new_folder_name):
        return get_module().Folder.rename(old_folder_name, new_folder_name)

    @classmethod
    def remove(cls, folder_name):
        return get_module().Folder.remove(folder_name)

    @classmethod
    def all(cls):
        return get_module().Folder.all()

    @classmethod
    def get_unique_match(cls, prefix):
        return get_module().Folder.get_unique_match(prefix)


class Todo(abstract.AbstractTodo):
    @classmethod
    def query(cls, **search_parameters):
        return get_module().Todo.query(**search_parameters)

    @classmethod
    def get_unique_match(cls, **search_parameters):
        return get_module().Todo.get_unique_match(**search_parameters)

    @classmethod
    def get_by_key(cls, id):
        return get_module().Todo.get_by_key(id)

    @classmethod
    def active_todos(cls):
        return get_module().Todo.active_todos()

    @classmethod
    def get_projects(cls, search_string):
        return get_module().Todo.get_projects(search_string)

    @classmethod
    def new(cls, **args):
        return get_module().Todo.new(**args)

    def save(self):
        return get_module().Todo.save()

    @classmethod
    def remove(cls, id):
        return get_module().Todo.remove(id)

    @classmethod
    def get_next_id(cls):
        return get_module().Todo.get_next_id()


class UndoStack():
    @classmethod
    def push(cls, transaction):
        return get_module().UndoStack.push(transaction)

    @classmethod
    def pop(cls):
        return get_module().UndoStack.pop()


class RedoStack():
    @classmethod
    def push(cls, transaction):
        return get_module().RedoStack.push(transaction)

    @classmethod
    def pop(cls):
        return get_module().RedoStack.pop()


class UnsyncedQueue:
    @classmethod
    def push(cls, transaction):
        return get_module().UnsyncedQueue.push(transaction)

    @classmethod
    def all_as_json(cls):
        return get_module().UnsyncedQueue.all_as_json()

    @classmethod
    def clear(cls):
        return get_module().UnsyncedQueue.clear()


class Client:
    @classmethod
    def get_client_id(cls):
        return get_module().Client.get_client_id()

    @classmethod
    def get_counter_increment(cls):
        return get_module().Client.get_counter_increment()


class SavedList(abstract.AbstractSavedList):
    @classmethod
    def get_most_recent(cls):
        return get_module().SavedList.get_most_recent()

    @classmethod
    def get_todos_in_list(cls, listname):
        return get_module().SavedList.get_todos_in_list(listname)

    @classmethod
    def get_todos_from_most_recent_search(cls):
        return get_module().SavedList.get_todos_from_most_recent_search()

    @classmethod
    def save_search(cls, name, todo_query):
        return get_module().SavedList.save_search(name, todo_query)

    @classmethod
    def save_most_recent_search(cls, todo_query):
        return get_module().SavedList.save_most_recent_search(todo_query)


class Database(abstract.AbstractDatabase):
    @classmethod
    def create(cls):
        return get_module().Database.create()

    @classmethod
    def connect(cls):
        return get_module().Database.connect()

    @classmethod
    def close(cls):
        return get_module().Database.close()

    @classmethod
    def update(cls):
        return get_module().Database.update()


def get_module():
    if ('database' in config.settings and
            'type' in config.settings['database']):
        if config.settings['database']['type'] in SQL_TYPES:
            return backend.db
    raise backend.DatabaseError("Invalid database configuration specified")
