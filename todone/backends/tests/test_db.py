from unittest import skip, TestCase

import peewee
from playhouse.test_utils import test_database

import todone
from todone.backends import folders
from todone.backends.db import Todo

in_memory_db = peewee.SqliteDatabase(':memory:')


class TestDatabaseTodoModel(TestCase):
    def setUp(self):
        todone.config.db = None

    def run(self, result=None):
        with test_database(in_memory_db, [Todo, ]):
            super().run(result)

    def test_class_is_importable(self):
        t = Todo(action='Blank')
        self.assertEqual(type(t), Todo)

    def test_todo_stores_action(self):
        t = Todo(action='New todo item')
        self.assertEqual(t.action, 'New todo item')
        t.save()

    def test_todo_raises_with_empty_action(self):
        with self.assertRaises(peewee.IntegrityError):
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

    def test_active_todos_restricts_select(self):
        todos = {}
        for n, folder in enumerate(folders.FOLDERS):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        active = Todo.active_todos()
        active_todos = [t for t in active]

        test_active = [folders.INBOX, folders.NEXT, folders.TODAY]
        test_inactive = [x for x in folders.FOLDERS if x not in test_active]
        for folder in test_inactive:
            self.assertNotIn(todos[folder], active_todos)
        for folder in test_active:
            self.assertIn(todos[folder], active_todos)

    @skip
    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError):
            t = Todo(action='Test', folder='invalid')
            t.save()
