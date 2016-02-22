import datetime
from unittest import TestCase

from todone.backends import folders
from todone.backends.flat import Todo

class TestFlatTodoModel(TestCase):

    def test_class_is_importable(self):
        t = Todo('Blank')
        self.assertEqual(type(t), Todo)

    def test_todo_stores_action(self):
        t = Todo('New todo item')
        self.assertEqual(t.action, 'New todo item')

    def test_todo_raises_with_empty_action(self):
        with self.assertRaises(ValueError) as context:
            t = Todo('')

    def test_todo_stores_valid_folder(self):
        for folder in [x for x in folders.FOLDERS]:
            t = Todo('Test todo', folder=folder)
            self.assertEqual(t.folder, folder)

    def test_todo_default_folder_is_inbox(self):
        t = Todo('Test')
        self.assertEqual(t.folder, folders.INBOX)

    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError) as context:
            t = Todo('Test', folder='invalid')
