import os
import peewee

from todone.config import settings

MOST_RECENT_SEARCH = 'last_search'
database = peewee.SqliteDatabase(None)


class BaseModel(peewee.Model):
    class Meta:
        database = database


class Todo(BaseModel):
    action = peewee.CharField(
        constraints=[peewee.Check("action != ''")],
    )
    folder = peewee.CharField(
        default=settings['folders']['default_inbox']
    )
    remind = peewee.DateField(
        null=True
    )
    # date_completed = peewee.DateField()
    due = peewee.DateField(null=True)
    # notes = peewee.CharField()
    # repeat_interval = peewee.CharField()

    def __str__(self):
        item = '- ' + self.folder + '/' + self.action
        return item

    def __repr__(self):
        output = '{}/{}'.format(self.folder, self.action)
        return output

    @classmethod
    def active_todos(cls):
        """
        Construct a select query of all active todos. Active
        todos are: inbox, next, and today.
        """
        active = cls.select().where(
            Todo.folder << settings['folders']['active']
        )
        return active


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


def create_database():
    database.create_tables([Todo,  SavedList, ListItem])


def initialize_database():
    database.init(os.path.expanduser(settings['database']['name']))


def connect_database():
    database.connect()


def close_database():
    database.close()
