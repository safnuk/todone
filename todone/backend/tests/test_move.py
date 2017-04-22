import datetime

from todone.backend import SavedList
from todone.backend.db import Todo as TodoSQL
from todone.backend.db import UndoStack
from todone.backend.commands import Move
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
        self.todos.append(TodoSQL.create(action='Sub item',
                                         parent=self.todos[4]))
        SavedList.save_most_recent_search(self.todos)

    def test_todo_moves_to_designated_folder(self):
        Move.run({'index': 1, 'folder': 'today'})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Todo 1')
        self.assertEqual(moved_todo.folder.name, 'today')

    def test_todo_should_move_out_of_project_when_no_parent_specified(self):
        Move.run({'index': 7, 'parent': {'folder': '', 'keywords': []}})
        moved_todo = TodoSQL.get(TodoSQL.action == 'Sub item')
        self.assertEqual(moved_todo.parent, None)

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

    def test_move_folder_returns_action_taken(self):
        status, response = Move.run({'index': 3, 'folder': 'done'})
        self.assertIn('Moved: Todo 3 -> {}'.format('done'), response)
        self.assertEqual(status, 'success')

    def test_move_parent_returns_action_taken(self):
        status, response = Move.run(
            {'index': 3,
             'parent': {'folder': 'today', 'keywords': ['project']}})
        self.assertIn('Moved: Todo 3 -> [{}]'.format('project'),
                      response)
        self.assertEqual(status, 'success')

    def test_invalid_index_returns_error_message(self):
        status, response = Move.run({'index': 8, 'folder': 'today'})
        self.assertEqual(status, 'error')

    def test_should_push_transaction_to_UndoStack(self):
        Move.run({'index': 1, 'folder': 'today'})
        self.assertEqual(len(UndoStack.select()), 1)

    def test_transaction_should_encode_folder_move(self):
        old_folder = self.todos[0].folder.name
        Move.run({'index': 1, 'folder': 'today'})
        transaction = UndoStack.pop()
        args = transaction.args
        self.assertEqual(transaction.command, 'move')
        self.assertEqual(args['old_folder'], old_folder)
        self.assertEqual(args['new_folder'], 'today')
        self.assertEqual(args['todo'], self.todos[0].id)

    def test_transaction_should_encode_parent_to_parent_move(self):
        old_parent = self.todos[4].id
        new_parent = self.todos[5].id
        Move.run({'index': 7, 'parent': {'folder': 'next',
                                         'keywords': ['other']}})
        transaction = UndoStack.pop()
        args = transaction.args
        self.assertEqual(transaction.command, 'move')
        self.assertEqual(args['old_parent'], old_parent)
        self.assertEqual(args['new_parent'], new_parent)
        self.assertEqual(args['todo'], self.todos[6].id)

    def test_transaction_should_encode_None_to_parent_move(self):
        old_parent = None
        new_parent = self.todos[4].id
        Move.run({'index': 1,
                  'parent': {'folder': '', 'keywords': ['project']}})
        transaction = UndoStack.pop()
        args = transaction.args
        self.assertEqual(transaction.command, 'move')
        self.assertEqual(args['old_parent'], old_parent)
        self.assertEqual(args['new_parent'], new_parent)
        self.assertEqual(args['todo'], self.todos[0].id)

    def test_transaction_should_encode_parent_to_None_move(self):
        old_parent = self.todos[4].id
        new_parent = None
        Move.run({'index': 7, 'parent': {'folder': '',
                                         'keywords': []}})
        transaction = UndoStack.pop()
        args = transaction.args
        self.assertEqual(transaction.command, 'move')
        self.assertEqual(args['old_parent'], old_parent)
        self.assertEqual(args['new_parent'], new_parent)
        self.assertEqual(args['todo'], self.todos[6].id)

    def test_new_transaction_should_record_timestamp(self):
        Move.run({'index': 1, 'folder': 'today'})
        now = datetime.datetime.now()
        transaction = UndoStack.pop()
        timediff = (now - transaction.timestamp).total_seconds()
        self.assertAlmostEqual(timediff, 0, delta=0.01)
