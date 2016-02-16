from contextlib import redirect_stdout
import io
from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone.commands import SCRIPT_DESCRIPTION
from todone.application import main
from todone.todos import folders
from todone.todos.db import Todo

in_memory_db = peewee.SqliteDatabase(':memory:')

class DB_Backend(TestCase):

    def run(self, result=None):
        with test_database(in_memory_db, [Todo,]):
            super().run(result)
        
    def test_help_arg_returns_help_string(self):
        f = io.StringIO()
        with redirect_stdout(f):
            main(['help'])
        s = f.getvalue()
        self.assertIn(SCRIPT_DESCRIPTION, s)

    def test_list_folder_restricts_to_correct_todos(self):
        todos = {}
        for n, folder in enumerate(folders.FOLDERS):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        f = io.StringIO()
        with redirect_stdout(f):
            main(['list'])
        s = f.getvalue()
        for folder in [x for x in folders.FOLDERS if x is not folders.TODAY]:
            self.assertNotIn(str(todos[folder]), s)
        self.assertIn(str(todos[folders.TODAY]), s)

        for list_folder in folders.FOLDERS:
            f = io.StringIO()
            with redirect_stdout(f):
                main(['list', list_folder])
            s = f.getvalue()
            for folder in [
                    x for x in folders.FOLDERS if x is not list_folder
            ]:
                self.assertNotIn(str(todos[folder]), s)
            self.assertIn(str(todos[list_folder]), s)


