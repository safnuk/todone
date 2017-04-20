from contextlib import redirect_stdout
import io

from todone.backend import SavedList
from todone.backend.db import Todo as TodoSQL
from todone.backend.commands import Move
import todone.exceptions as exceptions
from todone.tests.base import DB_Backend


class TestMoveTodo(DB_Backend):

    def setUp(self):
        self.todos = []
        self.todos.append(TodoSQL.create(action='Todo 1', folder='inbox'))
        self.todos.append(TodoSQL.create(action='Todo 2', folder='inbox'))
        self.todos.append(TodoSQL.create(action='Todo 3', folder='next'))
        self.todos.append(TodoSQL.create(action='Todo 4', folder='today'))
        self.todos.append(TodoSQL.create(action='project', folder='today'))
        self.todos.append(TodoSQL.create(action='other', folder='next'))
        SavedList.save_most_recent_search(self.todos)

    def test_todo_moves_to_designated_folder(self):
        Move.run({'index': 1, 'folder': 'today'})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'today')

    def test_todo_moves_to_designated_parent(self):
        Move.run(
            {'index': 1, 'parent': {'folder': '', 'keywords': ['project']}})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.parent.action, 'project')

    def test_todo_moves_from_one_to_another_parent(self):
        Move.run(
            {'index': 1,
             'parent': {'folder': 'today', 'keywords': ['project']}})
        Move.run(
            {'index': 1, 'parent': {'folder': 'next', 'keywords': ['other']}})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.parent.action, 'other')

    def test_changing_todo_parent_preserves_folder(self):
        Move.run(
            {'index': 1, 'parent': {'folder': '', 'keywords': ['project']}})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'inbox')

    def test_move_folder_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            Move.run({'index': 3, 'folder': 'done'})
        s = f.getvalue()
        self.assertIn('Moved: Todo 3 -> {}'.format('done'), s)

    def test_move_parent_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            Move.run(
                {'index': 3,
                 'parent': {'folder': 'today', 'keywords': ['project']}})
        s = f.getvalue()
        self.assertIn('Moved: Todo 3 -> [{}]'.format('project'), s)

    def test_invalid_index_displays_error_message(self):
        with self.assertRaises(exceptions.ArgumentError):
            Move.run({'index': 7, 'folder': 'today'})
