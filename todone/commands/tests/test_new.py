from contextlib import redirect_stdout
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from unittest import TestCase
import io

from todone.backends.db import Todo
from todone.commands.new import new_todo, parse_args
from todone.tests.base import DB_Backend


class TestNewAction(DB_Backend):

    def test_new_item_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            new_todo(['New todo'])
        s = f.getvalue()
        self.assertIn('Added: New todo to {}'.format('inbox'), s)

        f = io.StringIO()
        with redirect_stdout(f):
            new_todo(['today/', 'New todo 2'])
        s = f.getvalue()
        self.assertIn('Added: New todo 2 to {}'.format('today'), s)

    def test_new_item_saves_todo(self):
        new_todo(['Todo 1'])
        new_todo(['today/', 'Todo 2'])
        new_todo(['project/', 'Todo 3'])
        new_todo(['someday/', 'Todo 4'])
        todos = Todo.select()
        self.assertEqual(len(todos), 4)

    def test_new_item_saves_to_inbox_by_default(self):
        new_todo(['Todo 1'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder, 'inbox')

    def test_new_item_saves_to_specified_folder(self):
        new_todo(['today/Todo 1'])
        new_todo(['project/Todo 2'])
        new_todo(['someday/Todo 3'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder, 'today')
        t2 = Todo.get(Todo.action == 'Todo 2')
        self.assertEqual(t2.folder, 'project')
        t3 = Todo.get(Todo.action == 'Todo 3')
        self.assertEqual(t3.folder, 'someday')

    def test_new_item_saves_due_date(self):
        one_week = date.today() + timedelta(weeks=1)
        new_todo(['Todo 1', 'due+1w'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.due, one_week)


class TestNewArgParse(TestCase):

    def test_parse_args_defaults_to_inbox_folder(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['folder'], 'inbox')
        args = parse_args(['New', 'today/', 'todo'])
        self.assertEqual(args['folder'], 'inbox')

    def test_parse_args_parses_valid_folder(self):
        args = parse_args(['toDay/', 'New', 'todo'])
        self.assertEqual(args['folder'], 'today')
        args = parse_args(['iN/', 'today', 'todo'])
        self.assertEqual(args['folder'], 'inbox')
        args = parse_args(['iN/today', 'todo'])
        self.assertEqual(args['folder'], 'inbox')

    def test_parse_args_does_not_parse_invalid_folder(self):
        args = parse_args(['today', 'New', 'todo'])
        self.assertEqual(args['folder'], 'inbox')

    def test_parse_args_parsed_todo_title(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['action'], 'New todo')

    def test_parse_args_parses_due_keyword(self):
        today = date.today()
        args = parse_args(['due+1m', 'Test todo'])
        self.assertEqual(args['due'], today + relativedelta(months=1))
