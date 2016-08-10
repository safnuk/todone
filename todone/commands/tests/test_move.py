from contextlib import redirect_stdout
import io
from unittest import TestCase

from todone.backends.db import SavedList, Todo
from todone.commands.move import move_todo, parse_args
from todone.tests.base import DB_Backend
from todone.parser.textparser import ArgumentError


class TestMoveTodo(DB_Backend):

    def setUp(self):
        self.todos = []
        self.todos.append(Todo.create(action='Todo 1', folder='inbox'))
        self.todos.append(Todo.create(action='Todo 2', folder='inbox'))
        self.todos.append(Todo.create(action='Todo 3', folder='next'))
        self.todos.append(Todo.create(action='Todo 4', folder='today'))
        SavedList.save_most_recent_search(self.todos)

    def test_todo_moves_to_designated_folder(self):
        move_todo(['1', 'today/'])
        moved_todo = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'today')

    def test_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            move_todo(['3', 'done/'])
        s = f.getvalue()
        self.assertIn('Moved: "Todo 3" to {}'.format('done'), s)

    def test_invalid_index_displays_error_message(self):
        pass


class TestMoveArgParse(TestCase):

    def test_parses_integer(self):
        args = parse_args(['5', 'today/'])
        self.assertEqual(args['index'], 5)

    def test_negative_integer_does_not_match(self):
        with self.assertRaises(ArgumentError):
            parse_args(['-5', 'today/'])

    def test_parses_folder(self):
        args = parse_args(['0', 'in/'])
        self.assertEqual(args['folder'], 'inbox')
