from contextlib import redirect_stdout
import io
from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone.actions import SCRIPT_DESCRIPTION
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

    def test_default_list_is_today_items(self):
        t1 = Todo(action='Item 1', folder=folders.INBOX)
        t1.save()
        t2 = Todo(action='Item 2', folder=folders.NEXT)
        t2.save()
        t3 = Todo(action='Item 3', folder=folders.TODAY)
        t3.save()
        f = io.StringIO()
        with redirect_stdout(f):
            main(args=['list'])
        s = f.getvalue()
        self.assertNotIn('Item 1', s)
        self.assertNotIn('Item 2', s)
        self.assertIn('___ Item 3', s)


