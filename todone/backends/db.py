import datetime
import os
import re

import peewee

from todone.backends.abstract_backend import (
    AbstractDatabase,
    AbstractFolder,
    AbstractTodo,
)
from todone.backends.exceptions import DatabaseError
from todone import config
from todone.parser.textparser import ArgumentError

MOST_RECENT_SEARCH = 'last_search'


class Database(AbstractDatabase):
    database = peewee.SqliteDatabase(None)

    @classmethod
    def create(cls):
        try:
            cls.database.create_tables([Folder, Todo,  SavedList, ListItem])
            for folder in config.settings['folders']['default_folders']:
                Folder.create(name=folder)
        except peewee.OperationalError as e:
            if "already exists" in str(e):
                raise DatabaseError("Database already exists")
            else:
                raise DatabaseError("Could not create the database")

    @classmethod
    def connect(cls):
        # don't try to connect to a nameless database
        if config.settings['database']['name'] == '':
            return
        try:
            cls.database.init(
                os.path.expanduser(config.settings['database']['name']))
            cls.database.connect()
        except peewee.OperationalError:
            raise DatabaseError("Could not connect to the database")

    @classmethod
    def close(cls):
        try:
            if not cls.database.is_closed():
                cls.database.close()
        except peewee.OperationalError:
            raise DatabaseError("Could not close the database")

    @classmethod
    def update(cls):
        cls.close()
        cls.connect()


class BaseModel(peewee.Model):
    class Meta:
        database = Database.database


class Folder(BaseModel, AbstractFolder):
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
            raise DatabaseError('Database not setup properly')

    @classmethod
    def new(cls, folder):
        try:
            Folder.create(name=folder)
        except peewee.IntegrityError:
            raise ArgumentError(
                'Folder {}/ already exists'.format(folder))

    @classmethod
    def rename(cls, old_folder_name, new_folder_name):
        try:
            old_folder = Folder.get(Folder.name == old_folder_name)
        except peewee.DoesNotExist:
            raise ArgumentError(
                'No match found for folder {}/'.format(old_folder_name)
            )
        try:
            new_folder = Folder.create(name=new_folder_name)
        except peewee.IntegrityError:
            raise ArgumentError(
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
            raise ArgumentError(
                'Folder {} does not exist'.format(folder_name)
            )
        query = Todo.update(
            folder=config.settings['folders']['default_inbox']
        ).where(Todo.folder == folder)
        query.execute()
        folder.delete_instance()


class Todo(BaseModel, AbstractTodo):
    action = peewee.CharField(
        constraints=[peewee.Check("action != ''")],
    )
    folder = peewee.ForeignKeyField(
        Folder,
        default=config.settings['folders']['default_inbox'],
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
            Todo.create(**args)
        except peewee.OperationalError:
            raise DatabaseError('Error connecting to the database')

    @classmethod
    def query(cls, **args):
        results = Todo.select()
        if args['folder']:
            if args['folder'] in config.settings['folders']['today']:
                results = results.where(
                    (Todo.folder == args['folder']) |
                    (Todo.due <= datetime.date.today()) |
                    (Todo.remind <= datetime.date.today())
                ).where(
                    ~(Todo.folder << config.settings['folders']['inactive']))
            else:
                results = results.where(Todo.folder == args['folder'])
        else:
            results = Todo.active_todos()
        if args['parent']:
            results = results.where(Todo.parent << args['parent'])
        if args['due']:
            results = results.where(Todo.due <= args['due'])
        if args['remind']:
            results = results.where(Todo.remind <= args['remind'])
        for keyword in args['keywords']:
            results = results.where(Todo.action.contains(keyword))
        results = results.order_by(Todo.parent, -Todo.folder, Todo.id)
        return results

    @classmethod
    def active_todos(cls):
        """
        Construct a select query of all active todos. Active
        todos are: inbox, next, and today.
        """
        active = cls.select().where(
            Todo.folder << config.settings['folders']['active']
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


class SavedList(BaseModel):
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
