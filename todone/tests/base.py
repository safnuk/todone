import copy
from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone import config
from todone.backends.db import ListItem, SavedList, Todo

in_memory_db = peewee.SqliteDatabase(':memory:')


class DB_Backend(TestCase):

    def run(self, result=None):
        with test_database(in_memory_db, [Todo, SavedList, ListItem]):
            super().run(result)


class ResetSettings():

    def setUp(self):
        self.saved_settings = copy.deepcopy(config.settings)
        super().setUp()

    def tearDown(self):
        config.settings = self.saved_settings
        super().tearDown()
