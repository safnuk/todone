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
        for folder in [x for x in folders.FOLDERS if x != folders.REMIND]:
            t = Todo('Test todo', folder=folder)
            self.assertEqual(t.folder, folder)

    def test_todo_default_folder_is_inbox(self):
        t = Todo('Test')
        self.assertEqual(t.folder, folders.INBOX)

    def test_todo_raises_with_invalid_folder(self):
        with self.assertRaises(ValueError) as context:
            t = Todo('Test', folder='invalid')

    def test_remind_todos_store_date(self):
        today = datetime.date.today()
        t = Todo('Test', folder=folders.REMIND, remind_date=today)
        self.assertEqual(t.remind_date, today)

    def test_non_remind_todos_do_not_store_remind_date(self):
        t = Todo('Test')
        with self.assertRaises(AttributeError) as context:
            self.assertEqual(t.remind_date, None)

    def test_remind_items_withtout_date_raises(self):
        with self.assertRaises(ValueError) as context:
            t = Todo('Test', folder=folders.REMIND)
