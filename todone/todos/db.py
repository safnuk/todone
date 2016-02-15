import peewee

from todone.todos import folders

db = peewee.SqliteDatabase('db.sqlite3')

class Todo(peewee.Model):
    action = peewee.CharField()
    folder = peewee.CharField()
    remind_date = peewee.DateField()
    date_completed = peewee.DateField()
    due_date = peewee.DateField()
    notes = peewee.CharField()
    repeat_interval = peewee.CharField()

    def __str__(self):
        item = folders.PREFIXES[self.folder] + ' ' + self.action
        return item

    class Meta:
        database = db
