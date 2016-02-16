import datetime
from unittest import skip, TestCase
from unittest.mock import Mock, patch

import peewee
from playhouse.test_utils import test_database

from todone.todos import folders
from todone.todos.db import create_tables, Todo

in_memory_db = peewee.SqliteDatabase(':memory:')

class TestDatabaseTodoModel(TestCase):
    
    def run(self, result=None):
        with test_database(in_memory_db, [Todo,]):
            super().run(result)
        
    def test_class_is_importable(self):
        t = Todo(action='Blank')
        self.assertEqual(type(t), Todo)

    def test_todo_stores_action(self):
        t = Todo(action='New todo item')
        self.assertEqual(t.action, 'New todo item')
        t.save()

    def test_todo_raises_with_empty_action(self):
        with self.assertRaises(peewee.IntegrityError) as context:
            t = Todo(action='')
            t.save()

    def test_todo_stores_valid_folder(self):
        for folder in [x for x in folders.FOLDERS if x != folders.REMIND]:
            t = Todo(action='Test todo', folder=folder)
            t.save()
            self.assertEqual(t.folder, folder)

    def test_todo_default_folder_is_inbox(self):
        t = Todo(action='Test')
        t.save()
        self.assertEqual(t.folder, folders.INBOX)

    @skip
    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError) as context:
            t = Todo(action='Test', folder='invalid')
            t.save()
