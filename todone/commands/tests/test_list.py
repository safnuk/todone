from contextlib import redirect_stdout
from datetime import date, timedelta
import io
from unittest import skip, TestCase

from todone.backends import folders
from todone.backends.db import Todo
from todone.commands.list import list_items, parse_args
from todone.tests.base import DB_Backend


class TestListAction(DB_Backend):

    def test_list_folder_restricts_to_correct_todos(self):
        todos = {}
        for n, folder in enumerate(folders.FOLDERS):
            todos[folder] = Todo.create(
                action='Item {}'.format(n), folder=folder
            )
        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['t/'])
        s = f.getvalue()
        for folder in [x for x in folders.FOLDERS if x is not folders.TODAY]:
            self.assertNotIn(str(todos[folder]), s)
        self.assertIn(str(todos[folders.TODAY]), s)

        for list_folder in folders.FOLDERS:
            f = io.StringIO()
            with redirect_stdout(f):
                list_items([list_folder + '/'])
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
            list_items(['Item'])
        s = f.getvalue()
        active = [folders.INBOX, folders.NEXT, folders.TODAY]
        inactive = [x for x in folders.FOLDERS if x not in active]
        for folder in inactive:
            self.assertNotIn(str(todos[folder]), s)
        for folder in active:
            self.assertIn(str(todos[folder]), s)

    def test_list_today_includes_current_reminders(self):
        t1 = Todo.create(
            action='Test 1',
            folder=folders.INBOX,
            remind=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder=folders.NEXT,
            remind=date.today(),
            due=date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder=folders.TODAY,
            remind=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Grok 3',
            folder=folders.SOMEDAY,
            remind=date.today() - timedelta(days=2)
        )
        t5 = Todo.create(
            action='Sublime 4',
            folder=folders.DONE,
            remind=date.today() - timedelta(days=20)
        )
        t6 = Todo.create(
            action='Sublime 8',
            folder=folders.CANCEL,
            remind=date.today() - timedelta(days=20)
        )
        t7 = Todo.create(
            action='Sublime 5',
            folder=folders.NEXT,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['today/'])
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
            action='Test 1',
            folder=folders.INBOX,
            due=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder=folders.NEXT,
            remind=date.today() + timedelta(days=2),
            due=date.today() - timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder=folders.TODAY,
            due=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Grok 3',
            folder=folders.SOMEDAY,
            due=date.today() - timedelta(days=2)
        )
        t5 = Todo.create(
            action='Sublime 4',
            folder=folders.DONE,
            due=date.today() - timedelta(days=20)
        )
        t6 = Todo.create(
            action='Sublime 8',
            folder=folders.CANCEL,
            due=date.today() - timedelta(days=20)
        )
        t7 = Todo.create(
            action='Sublime 5',
            folder=folders.NEXT,
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['today/'])
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
            action='Test todo with search',
            folder=folders.INBOX
        )
        t2 = Todo.create(
            action='Test todo with grok',
            folder=folders.INBOX
        )
        t3 = Todo.create(
            action='Search todo for foo',
            folder=folders.TODAY
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['grok'])
        s = f.getvalue()
        self.assertNotIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['in/', 'test todo', 'with'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['test'])
        s = f.getvalue()
        self.assertIn(str(t1), s)
        self.assertIn(str(t2), s)
        self.assertNotIn(str(t3), s)

    def test_list_restricts_by_duedate(self):
        t1 = Todo.create(
            action='Test 1',
            folder=folders.INBOX,
            due=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder=folders.NEXT,
            remind=date.today(),
            due=date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder=folders.TODAY,
            due=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Sublime 4',
            folder=folders.NEXT,
            due=date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action='Sublime 5',
            folder=folders.NEXT,
        )
        t6 = Todo.create(
            action='Sublime 6',
            folder=folders.DONE,
            due=date.today()
        )
        t7 = Todo.create(
            action='Sublime 7',
            folder=folders.CANCEL,
            due=date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['due'])
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
            list_items(['due+15d'])
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
            list_items(['due+0d'])
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
            list_items(['due+3m'])
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
            action='Test 1',
            folder=folders.INBOX,
            remind=date.today()
        )
        t2 = Todo.create(
            action='Foo 2',
            folder=folders.NEXT,
            due=date.today(),
            remind=date.today() + timedelta(days=10)
        )
        t3 = Todo.create(
            action='Grok 3',
            folder=folders.TODAY,
            remind=date.today() - timedelta(days=2)
        )
        t4 = Todo.create(
            action='Sublime 4',
            folder=folders.NEXT,
            remind=date.today() + timedelta(days=20)
        )
        t5 = Todo.create(
            action='Sublime 5',
            folder=folders.NEXT,
        )
        t6 = Todo.create(
            action='Sublime 6',
            folder=folders.DONE,
            remind=date.today()
        )
        t7 = Todo.create(
            action='Sublime 7',
            folder=folders.CANCEL,
            remind=date.today()
        )

        f = io.StringIO()
        with redirect_stdout(f):
            list_items(['remind'])
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
            list_items(['remind+15d'])
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
            list_items(['remind+0d'])
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
            list_items(['remind+3m'])
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

    @skip
    def test_list_saves_last_search(self):
        self.fail("Write this test!")


class TestListArgParse(TestCase):

    def test_parse_args_parses_filename(self):
        args = parse_args(['.filename'])
        self.assertEqual(args['file'], 'filename')
        args = parse_args(['.filename', 'string1', '.string2'])
        self.assertEqual(args['file'], 'filename')
        args = parse_args(['string', 'filename'])
        self.assertEqual(args['file'], None)
        args = parse_args(['string1', 'string2', 'string.3'])
        self.assertEqual(args['file'], None)

    def test_parse_args_records_folder(self):
        args = parse_args(['today/'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['.file', 'today/'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['tod/', 'done'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['.file', 'string', 'today/'])
        self.assertFalse(args['folder'])
        args = parse_args(['string', 'today/'])
        self.assertFalse(args['folder'])

    def test_parse_args_parses_due_keyword(self):
        max_date = date(9999, 12, 31)
        args = parse_args(['due'])
        self.assertEqual(args['due'], max_date)
        args = parse_args(['.file', 'Due'])
        self.assertEqual(args['due'], max_date)
        args = parse_args(['.file', 'done', 'D+0d'])
        self.assertEqual(args['due'], date.today())
        args = parse_args(['.file', 'inbox', '@Work', 'r+5m', 'D+0d'])
        self.assertEqual(args['due'], date.today())

    def test_parse_args_parses_remind_keyword(self):
        max_date = date(9999, 12, 31)
        args = parse_args(['remind'])
        self.assertEqual(args['remind'], max_date)
        args = parse_args(['.file', 'remind'])
        self.assertEqual(args['remind'], max_date)
        args = parse_args(['.file', 'done', 'R+0d'])
        self.assertEqual(args['remind'], date.today())
        args = parse_args(['.file', 'inbox', '@Work', 'd+5m', 'r+0d'])
        self.assertEqual(args['remind'], date.today())

    def test_parse_args_parses_search_keywords(self):
        keywords = ['search', 'test', 'words']
        args = parse_args(keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file'] + keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file', 'today/'] + keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file', 'today/'] + keywords + ['due+3w'])
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(keywords + ['due+3w'] + ['.file', 'today/'])
        self.assertEqual(args['keywords'], keywords + ['.file', 'today/'])
        self.assertFalse(args['file'])
        self.assertFalse(args['folder'])
