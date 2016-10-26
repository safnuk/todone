from contextlib import redirect_stdout
import io
from unittest import TestCase
from unittest.mock import patch

from todone.application import main
from todone.tests.base import ResetSettings

TEST_DB = 'todone/tests/test.sqlite3'
CONFIG_DB = ['-c', 'todone/tests/config_db.ini']
BLANK_CONFIG_FILE = 'todone/tests/blank_config.ini'
BLANK_CONFIG_ARGS = ['-c', BLANK_CONFIG_FILE]


class FunctionalTestDB(ResetSettings, TestCase):

    def setUp(self):
        super().setUp()
        # clear test database
        with open(TEST_DB, 'w'):
            pass
        # clear blank config file
        with open(BLANK_CONFIG_FILE, 'w'):
            pass

    def run_todone(self, args):
        return self.run_todone_with_config(args, CONFIG_DB)

    def run_todone_with_config(self, args, config):
        f = io.StringIO()
        with redirect_stdout(f):
            main(config + args)
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
        s = self.run_todone(['setup', 'init'])
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

        # He moves the listed todo to the today folder
        s = self.run_todone(['move', '1', 'today/'])
        self.assertIn('Moved: "Another thing to do" to today', s)
        s = self.run_todone(['list', 'today/'])
        self.assertIn('Another thing to do', s)

    def test_project_functionality(self):
        # He sets up the database.
        s = self.run_todone(['setup', 'init'])
        self.maxDiff = None
        self.assertIn('New todone database initialized', s)

        # He creates a new project todo, and some sub-items
        self.run_todone(['new', 'next/', 'test project'])
        s1 = self.run_todone(['list', 'test project'])
        self.assertIn('test project', s1)
        s = self.run_todone(['new', '[test project]', 'Sub item the first'])
        s = self.run_todone(['new', 'Sub item the second', '[next/project]'])
        self.assertIn('Sub item the second', s)
        self.assertNotIn('project', s)

        # Listing the project shows the sub-items
        s = self.run_todone(['list', '[test project]'])
        self.assertIn('Sub item the first', s)
        self.assertIn('Sub item the second', s)
        s2 = self.run_todone(['list', '[next/project]'])
        self.assertEqual(s, s2)

    def test_folder_structure(self):
        # He sets up the database.
        s = self.run_todone(['setup', 'init'])

        # User tries to create a new todo, in a non-default folder
        s = self.run_todone(['new', 'testfolder/', 'New todo'])
        self.assertIn('Invalid argument', s)
        self.assertIn('No match found for folder testfolder/', s)

        # User then creates the new folder, and tries again to add a todo to it
        s = self.run_todone(['folder', 'new', 'testfolder/'])
        self.assertIn('Added folder: testfolder/', s)
        s = self.run_todone(['new', 'test/', 'New todo'])
        self.assertIn('Added: New todo to testfolder', s)

        # Listing the folder shows the todo
        s = self.run_todone(['list', 'testfolder/'])
        self.assertIn('New todo', s)

        # He creates another closely-named folder
        s = self.run_todone(['folder', 'new', 'testfolder1/'])
        self.assertIn('Added folder: testfolder1/', s)

        # Trying to add a todo to an ambiguous folder does not work
        s = self.run_todone(['new', 'test/', 'Another todo'])
        self.assertIn('Invalid argument', s)
        self.assertIn('Multiple matches found for folder test/', s)

        # He renames the folder, and sees that the todo in it reflects the
        # change
        s = self.run_todone(['folder', 'rename', 'testfolder/', 'myfolder/'])
        self.assertIn('Renamed folder: testfolder/ -> myfolder/', s)
        s = self.run_todone(['list', 'myfolder/'])
        self.assertIn('New todo', s)

        # He deletes the folder. The associated todo is moved to inbox/
        s = self.run_todone(['folder', 'delete', 'myfolder/'])
        self.assertIn('Deleted folder: myfolder/', s)
        s = self.run_todone(['list', 'inbox/'])
        self.assertIn('New todo', s)

    @patch('builtins.input', side_effect=[TEST_DB])
    def test_default_config_setup(self, mock_input):
        # User sets up db with blank config file, and is prompted for name
        # of database file to use
        s = self.run_todone_with_config(['setup', 'init'], BLANK_CONFIG_ARGS)
        self.assertIn('Created basic config file', s)
        self.assertIn('New todone database initialized', s)
