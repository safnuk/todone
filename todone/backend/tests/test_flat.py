from unittest import TestCase

from todone.backend import DEFAULT_FOLDERS
from todone.backend.flat import Todo


class TestFlatTodoModel(TestCase):

    def test_class_is_importable(self):
        t = Todo('Blank')
        self.assertEqual(type(t), Todo)

    def test_todo_stores_action(self):
        t = Todo('New todo item')
        self.assertEqual(t.action, 'New todo item')

    def test_todo_raises_with_empty_action(self):
        with self.assertRaises(ValueError):
            t = Todo('')
            assert(t)

    def test_todo_stores_valid_folder(self):
        for folder in [x for x in DEFAULT_FOLDERS['folders']]:
            t = Todo('Test todo', folder=folder)
            self.assertEqual(t.folder, folder)

    def test_todo_default_folder_is_inbox(self):
        t = Todo('Test')
        self.assertEqual(t.folder, DEFAULT_FOLDERS['folders'])

    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError):
            t = Todo('Test', folder='invalid')
            assert(t)
