"""Implementation of todone's backend API for accessing SQL databases.

Uses the peewee package to connect to databases.
"""
import json
import os
import re

import peewee

from todone.backend import abstract_backend as abstract
from todone.backend import transaction
from todone import backend
from todone import config
from todone import exceptions
from todone.parser import exceptions as pe

MOST_RECENT_SEARCH = 'last_search'


class Database(abstract.AbstractDatabase):
    database = peewee.Proxy()

    @classmethod
    def create(cls):
        try:
            cls.initialize()
            cls.database.create_tables(
                [Folder, Todo,  SavedList, ListItem, UndoStack, RedoStack])
            for folder in backend.DEFAULT_FOLDERS['folders']:
                Folder.create(name=folder)
        except Exception as e:
            if "already exists" in str(e):
                raise backend.DatabaseError("Database already exists")
            else:
                raise backend.DatabaseError("Could not create the database")

    @classmethod
    def initialize(cls):
        dbname = config.settings['database']['name']
        options = {key: value for key, value in
                   config.settings['database'].items()
                   if key not in ['type', 'name']}
        if config.settings['database']['type'] == 'sqlite3':
            db = peewee.SqliteDatabase(os.path.expanduser(dbname), **options)
        elif config.settings['database']['type'] == 'postgresql':
            db = peewee.PostgresqlDatabase(dbname, **options)

        cls.database.initialize(db)

    @classmethod
    def connect(cls):
        # don't try to connect to a nameless database
        if config.settings['database']['name'] == '':
            raise backend.DatabaseError(
                "Valid database location not configured")
        try:
            cls.initialize()
            cls.database.connect()
        except peewee.OperationalError:
            raise backend.DatabaseError("Could not connect to the database")

    @classmethod
    def close(cls):
        try:
            if not cls.database.is_closed():
                cls.database.close()
        except peewee.OperationalError:
            raise backend.DatabaseError("Could not close the database")

    @classmethod
    def update(cls):
        cls.connect()


class BaseModel(peewee.Model):
    class Meta:
        database = Database.database


class Folder(BaseModel, abstract.AbstractFolder):
    name = peewee.CharField(
        constraints=[peewee.Check("name != ''")],
        unique=True,
        primary_key=True
    )

    @classmethod
    def all(cls):
        try:
            return [f for f in cls.select()]
        except peewee.OperationalError:
            raise backend.DatabaseError('Database not setup properly')

    @classmethod
    def new(cls, folder):
        try:
            Folder.create(name=folder)
        except peewee.IntegrityError:
            raise pe.ArgumentError(
                'Folder {}/ already exists'.format(folder))

    @classmethod
    def rename(cls, old_folder_name, new_folder_name):
        try:
            old_folder = Folder.get(Folder.name == old_folder_name)
        except peewee.DoesNotExist:
            raise pe.ArgumentError(
                'No match found for folder {}/'.format(old_folder_name)
            )
        try:
            new_folder = Folder.create(name=new_folder_name)
        except peewee.IntegrityError:
            raise pe.ArgumentError(
                'Folder {}/ already exists'.format(new_folder_name))
        query = Todo.update(folder=new_folder).where(
            Todo.folder == old_folder
        )
        query.execute()
        old_folder.delete_instance()

    @classmethod
    def remove(cls, folder_name):
        try:
            folder = Folder.get(Folder.name == folder_name)
        except peewee.DoesNotExist:
            raise pe.ArgumentError(
                'Folder {} does not exist'.format(folder_name)
            )
        # if left as a query, will be empty by the time it is run
        todos_moved = list(Todo.select().where(Todo.folder == folder))
        query = Todo.update(
            folder=backend.DEFAULT_FOLDERS['inbox']
        ).where(Todo.folder == folder)
        query.execute()
        folder.delete_instance()
        return todos_moved

    @classmethod
    def get_unique_match(cls, prefix):
        matches = Folder.select().where(Folder.name.startswith(prefix))
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            raise backend.DatabaseError("No match found")
        else:
            raise backend.DatabaseError("Multiple matches found")


class Todo(BaseModel, abstract.AbstractTodo):
    action = peewee.CharField(
        constraints=[peewee.Check("action != ''")],
    )
    folder = peewee.ForeignKeyField(
        Folder,
        default=backend.DEFAULT_FOLDERS['inbox'],
        related_name='todos'
    )
    parent = peewee.ForeignKeyField(
        'self', null=True, related_name='subitems'
    )
    remind = peewee.DateField(
        null=True
    )
    # date_completed = peewee.DateField()
    due = peewee.DateField(null=True)
    # notes = peewee.CharField()
    # repeat_interval = peewee.CharField()

    def __str__(self):
        item = '- ' + self.folder.name + '/' + self.action
        return item

    def __repr__(self):
        output = '{}/{}'.format(self.folder, self.action)
        return output

    @classmethod
    def new(cls, **args):
        try:
            return Todo.create(**args)
        except peewee.OperationalError:
            raise backend.DatabaseError('Error connecting to the database')

    @classmethod
    def query(cls, **args):
        results = Todo.select()
        if args.get('folder'):
            results = results.where(Todo.folder == args['folder'])
        else:
            results = Todo.active_todos()
        if args.get('parent'):
            results = results.where(Todo.parent << args['parent'])
        if args.get('due'):
            results = results.where(Todo.due <= args['due'])
        if args.get('remind'):
            results = results.where(Todo.remind <= args['remind'])
        for keyword in args.get('keywords', []):
            results = results.where(Todo.action.contains(keyword))
        results = results.order_by(Todo.parent, -Todo.folder, Todo.id)
        return results

    @classmethod
    def get_unique_match(cls, **args):
        matches = cls.query(**args)
        if len(matches) == 1:
            return matches[0]
        elif len(matches) == 0:
            raise backend.DatabaseError("No match found")
        else:
            raise backend.DatabaseError("Multiple matches found")

    @classmethod
    def get_by_key(cls, id):
        try:
            return cls.get(Todo.id == id)
        except peewee.DoesNotExist:
            raise backend.DatabaseError("No match found")

    @classmethod
    def active_todos(cls):
        """
        Construct a select query of all active todos. Active
        todos are: inbox, next, and today.
        """
        active = cls.select().where(
            Todo.folder << backend.DEFAULT_FOLDERS['active']
        )
        return active

    @classmethod
    def get_projects(cls, search_string):
        query = Todo.select()
        folder_regex = r'\s*(?P<folder>[^\s/]+)/\s*(?P<todo>.+)'
        match = re.fullmatch(folder_regex, search_string)
        if match:
            query = query.where(
                Todo.folder == match.group('folder'),
                Todo.action.contains(match.group('todo'))
            )
        else:
            query = query.where(Todo.action.contains(search_string))
        return query


class SavedList(BaseModel, abstract.AbstractSavedList):
    name = peewee.CharField(
        constraints=[peewee.Check("name != ''")],
        unique=True,
    )

    @classmethod
    def get_most_recent(cls):
        recent, _ = cls.get_or_create(name=MOST_RECENT_SEARCH)
        return recent

    @classmethod
    def get_todos_in_list(cls, listname):
        listname = listname if listname else MOST_RECENT_SEARCH
        try:
            savedlist = SavedList.get(SavedList.name == listname)
            items = ListItem.select().where(ListItem.savedlist == savedlist)
            return [x.todo for x in items]
        except SavedList.DoesNotExist:
            return []

    @classmethod
    def get_todos_from_most_recent_search(cls):
        return cls.get_todos_in_list(MOST_RECENT_SEARCH)

    @classmethod
    def save_search(cls, name, todo_query):
        if not name:
            return
        savelist, _ = SavedList.get_or_create(name=name)
        savelist.delete_items()
        for todo in todo_query:
            ListItem.create(savedlist=savelist, todo=todo)

    @classmethod
    def save_most_recent_search(cls, todo_query):
        cls.save_search(MOST_RECENT_SEARCH, todo_query)

    def delete_items(self):
        items_to_delete = ListItem.delete().where(ListItem.savedlist == self)
        items_to_delete.execute()


class ListItem(BaseModel):
    savedlist = peewee.ForeignKeyField(SavedList, related_name='items')
    todo = peewee.ForeignKeyField(Todo)


class TransactionStack(abstract.AbstractCommandStack):
    @classmethod
    def push(cls, transaction):
        args = json.dumps(transaction.args)
        cls.create(command=transaction.command, args=args,
                   timestamp=transaction.timestamp)

    @classmethod
    def pop(cls):
        try:
            item = cls._get_first()
            item.delete_instance()
        except peewee.DoesNotExist:
            raise exceptions.DatabaseError(cls.error_msg)
        args = json.loads(item.args)
        return transaction.Transaction(item.command, args)


class UndoStack(BaseModel, TransactionStack):
    command = peewee.CharField()
    args = peewee.CharField()
    timestamp = peewee.DateTimeField()

    error_msg = 'Transaction history is empty'

    @classmethod
    def _get_first(cls):
        return cls.select().order_by(cls.timestamp.desc()).get()


class RedoStack(BaseModel, TransactionStack):
    command = peewee.CharField()
    args = peewee.CharField()
    timestamp = peewee.DateTimeField()

    error_msg = 'Redo history is empty'

    @classmethod
    def _get_first(cls):
        return cls.select().order_by(cls.timestamp.asc()).get()
