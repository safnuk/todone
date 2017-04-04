import todone.config as config
from todone.backend.abstract_backend import (
    AbstractDatabase,
    AbstractFolder,
    AbstractSavedList,
    AbstractTodo,
)
from todone.backend import DatabaseError
# from .db import DatabaseSQL, FolderSQL, ListItemSQL, SavedListSQL, TodoSQL
import todone

SQL_TYPES = ['sqlite3', 'postgresql']


class Folder(AbstractFolder):
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


class Todo(AbstractTodo):
    @classmethod
    def query(cls, **search_parameters):
        return get_module().Todo.query(**search_parameters)

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


class SavedList(AbstractSavedList):
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


class Database(AbstractDatabase):
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
            return todone.backend.db
    raise DatabaseError("Invalid database configuration specified")
