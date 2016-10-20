from contextlib import redirect_stdout
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
import io
from unittest import TestCase
from unittest.mock import patch

from todone.backends.db import Todo
from todone.commands.new import new_todo, parse_args
from todone.tests.base import DB_Backend, FolderMock
from todone.parser.textparser import ArgumentError


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
        new_todo(['done/', 'Todo 3'])
        new_todo(['someday/', 'Todo 4'])
        todos = Todo.select()
        self.assertEqual(len(todos), 4)

    def test_new_item_saves_to_inbox_by_default(self):
        new_todo(['Todo 1'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder.name, 'inbox')

    def test_new_item_saves_to_specified_folder(self):
        new_todo(['today/Todo 1'])
        new_todo(['done/Todo 2'])
        new_todo(['someday/Todo 3'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder.name, 'today')
        t2 = Todo.get(Todo.action == 'Todo 2')
        self.assertEqual(t2.folder.name, 'done')
        t3 = Todo.get(Todo.action == 'Todo 3')
        self.assertEqual(t3.folder.name, 'someday')

    def test_new_item_saves_due_date(self):
        one_week = date.today() + timedelta(weeks=1)
        new_todo(['Todo 1', 'due+1w'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.due, one_week)

    def test_new_item_saves_project(self):
        project = Todo.create(action='Project')
        new_todo(['Test todo', '[Project]'])
        t1 = Todo.get(Todo.action == 'Test todo')
        self.assertEqual(t1.parent, project)

    def test_raises_ArgumentError_when_saving_to_nonexisting_folder(self):
        with self.assertRaises(ArgumentError):
            new_todo(['nonfolder/', 'New todo'])
        with self.assertRaises(ArgumentError):
            new_todo(['nonfolder/'])


@patch('todone.commands.new.Folder', FolderMock)
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

    @patch('todone.commands.new.Todo')
    def test_parses_project_and_calls_get_project_todo(self, MockTodo):
        args = parse_args(['Test todo', '[project]'])
        self.assertEqual(
            args['parent'], MockTodo.get_projects('project').__getitem__(0)
        )
