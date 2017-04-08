from contextlib import redirect_stdout
import io
from unittest import TestCase

from todone.backend import SavedList
from todone.backend.db import Todo
from todone.commands.done import done_todo, parse_args
from todone.tests.base import DB_Backend
from todone.parser import exceptions as pe


class TestDoneTodo(DB_Backend):

    def setUp(self):
        self.todos = []
        self.todos.append(Todo.create(action='Todo 1', folder='inbox'))
        self.todos.append(Todo.create(action='Todo 2', folder='inbox'))
        self.todos.append(Todo.create(action='Todo 3', folder='next'))
        self.todos.append(Todo.create(action='Todo 4', folder='today'))
        self.todos.append(Todo.create(action='project', folder='today'))
        self.todos.append(Todo.create(action='other', folder='next'))
        SavedList.save_most_recent_search(self.todos)

    def test_todo_done_moves_todo_to_done_folder(self):
        done_todo(['1'])
        moved_todo = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'done')

    def test_done_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            done_todo(['3'])
        s = f.getvalue()
        self.assertIn('Moved: Todo 3 -> {}'.format('done'), s)


class TestDoneArgParse(TestCase):

    def test_parses_integer(self):
        args = parse_args(['5'])
        self.assertEqual(args['index'], 5)

    def test_negative_integer_does_not_match(self):
        with self.assertRaises(pe.ArgumentError):
            parse_args(['-5'])

    def test_rejects_noninteger_index(self):
        with self.assertRaises(pe.ArgumentError):
            parse_args(['test'])

    def test_rejects_two_args(self):
        with self.assertRaises(pe.ArgumentError):
            parse_args(['1', '2'])
        with self.assertRaises(pe.ArgumentError):
            parse_args(['1', 'test'])
