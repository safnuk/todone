from contextlib import redirect_stdout
import io

from todone.backend import SavedList
from todone.backend.db import Todo as TodoSQL
from todone.backend.commands.move import move_todo
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
        move_todo(['1', 'today/'])
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'today')

    def test_todo_moves_to_designated_parent(self):
        move_todo(['1', '[project]'])
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.parent.action, 'project')

    def test_todo_moves_from_one_to_another_parent(self):
        move_todo(['1', '[today/project]'])
        move_todo(['1', '[next/other]'])
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.parent.action, 'other')

    def test_changing_todo_parent_preserves_folder(self):
        move_todo(['1', '[project]'])
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'inbox')

    def test_move_folder_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            move_todo(['3', 'done/'])
        s = f.getvalue()
        self.assertIn('Moved: Todo 3 -> {}'.format('done'), s)

    def test_move_parent_prints_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            move_todo(['3', '[today/project]'])
        s = f.getvalue()
        self.assertIn('Moved: Todo 3 -> [{}]'.format('project'), s)

    def test_invalid_index_displays_error_message(self):
        pass