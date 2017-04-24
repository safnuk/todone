from todone.backend import SavedList
from todone.backend.db import Todo
from todone.backend.commands import Done
from todone.tests.base import DB_Backend


class TestDoneTodo(DB_Backend):

    def setUp(self):
        self.todos = []
        self.todos.append(Todo.new(action='Todo 1', folder='inbox'))
        self.todos.append(Todo.new(action='Todo 2', folder='inbox'))
        self.todos.append(Todo.new(action='Todo 3', folder='next'))
        self.todos.append(Todo.new(action='Todo 4', folder='today'))
        self.todos.append(Todo.new(action='project', folder='today'))
        self.todos.append(Todo.new(action='other', folder='next'))
        SavedList.save_most_recent_search(self.todos)

    def test_todo_done_moves_todo_to_done_folder(self):
        Done.run({'index': 1})
        moved_todo = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'done')

    def test_done_returns_action_taken(self):
        status, response = Done.run({'index': 3})
        self.assertEqual(status, 'success')
        self.assertIn('Moved: Todo 3 -> {}'.format('done'), response)
