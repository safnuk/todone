import peewee

from todone import config
from todone.backends import folders

db = peewee.SqliteDatabase(config.db['name'])


class BaseModel(peewee.Model):
    class Meta:
        database = db


class Todo(BaseModel):
    action = peewee.CharField(
        constraints=[peewee.Check("action != ''")],
    )
    folder = peewee.CharField(
        default = folders.INBOX,
    )
    # remind_date = peewee.DateField()
    # date_completed = peewee.DateField()
    # due_date = peewee.DateField()
    # notes = peewee.CharField()
    # repeat_interval = peewee.CharField()

    def __str__(self):
        item = folders.PREFIXES[self.folder] + ' ' + self.action
        return item


def create_tables():
    db.create_tables([Todo,])
