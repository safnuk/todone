from contextlib import redirect_stdout
import io
from unittest import TestCase

from todone.application import main
# from todone.backends import folders

TEST_DB = 'tests/test.sqlite3'
CONFIG_DB = ['-c', 'tests/config_db.ini']


class FunctionalTestDB(TestCase):

    def setUp(self):
        # clear test database
        with open(TEST_DB, 'w'):
            pass

    def run_todone(self, args):
        f = io.StringIO()
        with redirect_stdout(f):
            main(CONFIG_DB + args)
        return f.getvalue()

    def test_basic_usage(self):
        # User requests help, and sees a help message.
        s = self.run_todone(['help'])
        self.assertNotIn('Invalid argument(s)', s)
        self.assertIn('todo-list manager', s)

        # He tries to enter a new todo item, but is told that
        # the database is not setup yet.
        s = self.run_todone(['new', 'New todo'])
        self.assertIn('Cannot find valid database', s)

        # He sets up the database.
        s = self.run_todone(['setup'])
        self.assertIn('New todone database initialized', s)

        # He successfully adds a new todo.
        s = self.run_todone(['new', 'New todo'])
        self.assertIn('New todo to inbox', s)

        # He lists the inbox, and sees his new todo printed.
        s = self.run_todone(['list', 'inbox/'])
        self.assertIn('New todo', s)

        # He adds another todo, this time a next action
        s = self.run_todone(['new', 'next/', 'Another thing to do'])
        self.assertIn('Another thing to do to next', s)

        # The todos appear only in their respective folders when listed.
        s = self.run_todone(['list', 'inbox/'])
        self.assertIn('New todo', s)
        self.assertNotIn('Another thing to do', s)
        s = self.run_todone(['list', 'next/'])
        self.assertNotIn('New todo', s)
        self.assertIn('Another thing to do', s)

        # He uses the last-list save feature
        s = self.run_todone(['list'])
        self.assertNotIn('New todo', s)
        self.assertIn('Another thing to do', s)

        # Next he creates a saved search
        s = self.run_todone(['list', '.next', 'next/'])
        self.assertNotIn('New todo', s)
        self.assertIn('Another thing to do', s)

        s = self.run_todone(['list', 'today/'])
        self.assertNotIn('New todo', s)
        self.assertNotIn('Another thing to do', s)

        # He lists the saved search
        s = self.run_todone(['list', '.next'])
        self.assertNotIn('New todo', s)
        self.assertIn('Another thing to do', s)

        # The default search should be a repeat
        s = self.run_todone(['list'])
        self.assertNotIn('New todo', s)
        self.assertIn('Another thing to do', s)
