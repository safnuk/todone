from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone.backends.db import ListItem, SavedList, Todo

in_memory_db = peewee.SqliteDatabase(':memory:')


class DB_Backend(TestCase):

    def run(self, result=None):
        with test_database(in_memory_db, [Todo, SavedList, ListItem]):
            super().run(result)
