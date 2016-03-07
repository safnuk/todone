from contextlib import redirect_stdout
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from unittest import TestCase
import io

from todone.application import main
from todone.backends import folders
from todone.backends.db import Todo
from todone.commands.new import parse_args
from todone.tests.base import DB_Backend


class TestNewAction(DB_Backend):

    def test_new_item_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            main(['new', 'New todo'])
        s = f.getvalue()
        self.assertIn('Added: New todo to {}'.format(folders.INBOX), s)

        f = io.StringIO()
        with redirect_stdout(f):
            main(['new', 'today', 'New todo 2'])
        s = f.getvalue()
        self.assertIn('Added: New todo 2 to {}'.format(folders.TODAY), s)

    def test_new_item_saves_todo(self):
        main(['new', 'Todo 1'])
        main(['new', 'today', 'Todo 2'])
        main(['new', 'project', 'Todo 3'])
        main(['new', 'someday', 'Todo 4'])
        todos = Todo.select()
        self.assertEqual(len(todos), 4)

    def test_todos_must_be_unique_to_projects(self):
        pass

    def test_new_item_saves_to_inbox_by_default(self):
        main(['new', 'Todo 1'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder, folders.INBOX)

    def test_new_item_saves_due_date(self):
        one_week = date.today() + timedelta(weeks=1)
        main(['new', 'Todo 1', 'due+1w'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.due, one_week)


class TestNewArgParse(TestCase):

    def test_parse_args_defaults_to_inbox_folder(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)
        args = parse_args(['New', 'today', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_parses_valid_folder(self):
        args = parse_args(['toDay', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['iN', 'today', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_does_not_parse_invalid_folder(self):
        args = parse_args(['done', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

        args = parse_args(['cancel', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_parsed_todo_title(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['action'], 'New todo')

    def test_parse_args_parses_due_keyword(self):
        today = date.today()
        args = parse_args(['due+1m', 'Test todo'])
        self.assertEqual(args['due'], today + relativedelta(months=1))
