import os
import peewee

from todone.config import settings

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


def create_database():
    database.create_tables([Todo, ])


def initialize_database():
    database.init(os.path.expanduser(settings['database']['name']))


def connect_database():
    database.connect()


def close_database():
    database.close()
