import copy
from unittest import TestCase
from unittest.mock import Mock

import peewee
from playhouse.test_utils import test_database

from todone import config
from todone.backend import (
    DEFAULT_FOLDERS,
)
from todone.backend.db import ListItem, Folder, SavedList, Todo

in_memory_db = peewee.SqliteDatabase(':memory:')


class FakeFolder():
    def __init__(self, name):
        self.name = name


FolderMock = Mock()
FolderMock.all.return_value = [
    FakeFolder(name) for name in DEFAULT_FOLDERS['folders']
]


class DB_Backend(TestCase):

    def run(self, result=None):
        with test_database(in_memory_db, [Folder, Todo, SavedList, ListItem]):
            for folder in DEFAULT_FOLDERS['folders']:
                Folder.create(name=folder)
            super().run(result)


class ResetSettings():

    def setUp(self):
        self.saved_settings = copy.deepcopy(config.settings)
        self.saved_file = copy.deepcopy(config.config_file)
        super().setUp()

    def tearDown(self):
        config.settings = self.saved_settings
        config.config_file = self.saved_file
        super().tearDown()
