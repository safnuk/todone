from contextlib import redirect_stdout
from datetime import date, timedelta
import io
from unittest import skip, TestCase

import peewee
from playhouse.test_utils import test_database

from todone.application import main, SCRIPT_DESCRIPTION
from todone.backends import folders
from todone.backends.db import Todo

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
            main(['list', 't'])
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


    def test_list_without_folder_restricts_to_active_todos(self):
        todos = {}
        for n, folder in enumerate(folders.FOLDERS):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'Item'])
        s = f.getvalue()
        active = [folders.INBOX, folders.NEXT, folders.TODAY]
        inactive = [x for x in folders.FOLDERS if x not in active]
        for folder in inactive:
            self.assertNotIn(str(todos[folder]), s)
        for folder in active:
            self.assertIn(str(todos[folder]), s)


    def test_list_today_includes_current_reminders(self):
        t1 = Todo.create(
            action = 'Test 1',
            folder = folders.INBOX,
            remind_date = date.today()
        )
        t2 = Todo.create(
            action = 'Foo 2',
            folder = folders.NEXT,
            remind_date = date.today(),
            due_date = date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action = 'Grok 3',
            folder = folders.TODAY,
            remind_date = date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action = 'Grok 3',
            folder = folders.SOMEDAY,
            remind_date = date.today() - timedelta(days=2)
        )
        t5 = Todo.create(
            action = 'Sublime 4',
            folder = folders.DONE,
            remind_date = date.today() - timedelta(days=20)
        )
        t6 = Todo.create(
            action = 'Sublime 8',
            folder = folders.CANCEL,
            remind_date = date.today() - timedelta(days=20)
        )
        t7 = Todo.create(
            action = 'Sublime 5',
            folder = folders.NEXT,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'today'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)


    def test_list_today_includes_due_items(self):
        t1 = Todo.create(
            action = 'Test 1',
            folder = folders.INBOX,
            due_date = date.today()
        )
        t2 = Todo.create(
            action = 'Foo 2',
            folder = folders.NEXT,
            remind_date = date.today() + timedelta(days=2),
            due_date = date.today() - timedelta(days=10)
        )
        t3 = Todo.create(
            action = 'Grok 3',
            folder = folders.TODAY,
            due_date = date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action = 'Grok 3',
            folder = folders.SOMEDAY,
            due_date = date.today() - timedelta(days=2)
        )
        t5 = Todo.create(
            action = 'Sublime 4',
            folder = folders.DONE,
            due_date = date.today() - timedelta(days=20)
        )
        t6 = Todo.create(
            action = 'Sublime 8',
            folder = folders.CANCEL,
            due_date = date.today() - timedelta(days=20)
        )
        t7 = Todo.create(
            action = 'Sublime 5',
            folder = folders.NEXT,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'today'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)


    def test_list_restricts_by_search_keywords(self):
        t1 = Todo.create(
            action = 'Test todo with search',
            folder = folders.INBOX
        )
        t2 = Todo.create(
            action = 'Test todo with grok',
            folder = folders.INBOX
        )
        t3 = Todo.create(
            action = 'Search todo for foo',
            folder = folders.TODAY
        )

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'grok'])
        s = f.getvalue()
        self.assertNotIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'in', 'test todo', 'with'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'test'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

    def test_list_restricts_by_duedate(self):
        t1 = Todo.create(
            action = 'Test 1',
            folder = folders.INBOX,
            due_date = date.today()
        )
        t2 = Todo.create(
            action = 'Foo 2',
            folder = folders.NEXT,
            remind_date = date.today(),
            due_date = date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action = 'Grok 3',
            folder = folders.TODAY,
            due_date = date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action = 'Sublime 4',
            folder = folders.NEXT,
            due_date = date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action = 'Sublime 5',
            folder = folders.NEXT,
        )
        t6 = Todo.create(
            action = 'Sublime 6',
            folder = folders.DONE,
            due_date = date.today()
        )
        t7 = Todo.create(
            action = 'Sublime 7',
            folder = folders.CANCEL,
            due_date = date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'due'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'due+15d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'due+0d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'due+3m'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)


    def test_list_restricts_by_remind_date(self):
        t1 = Todo.create(
            action = 'Test 1',
            folder = folders.INBOX,
            remind_date = date.today()
        )
        t2 = Todo.create(
            action = 'Foo 2',
            folder = folders.NEXT,
            due_date = date.today(),
            remind_date = date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action = 'Grok 3',
            folder = folders.TODAY,
            remind_date = date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action = 'Sublime 4',
            folder = folders.NEXT,
            remind_date = date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action = 'Sublime 5',
            folder = folders.NEXT,
        )
        t6 = Todo.create(
            action = 'Sublime 6',
            folder = folders.DONE,
            remind_date = date.today()
        )
        t7 = Todo.create(
            action = 'Sublime 7',
            folder = folders.CANCEL,
            remind_date = date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'remind'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'remind+15d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'remind+0d'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertNotIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertNotIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['list', 'remind+3m'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertIn(str(t3), s)
        self.assertIn(str(t4), s)
        self.assertNotIn(str(t5), s)
        self.assertNotIn(str(t6), s)
        self.assertNotIn(str(t7), s)


    @skip
    def test_list_restricts_by_cal_date(self):
        self.fail("Write this test!")


    @skip
    def test_list_restricts_by_project(self):
        self.fail("Write this test!")

