import datetime
from datetime import date, timedelta
from unittest import skip

from todone.backend.db import Todo, UndoStack
from todone.backend.commands import New
from todone.tests.base import DB_Backend


class TestNewAction(DB_Backend):

    def test_new_item_returns_action_taken(self):
        s, r = New.run({'action': 'New todo'})
        self.assertEqual(s, 'success')
        self.assertIn('Added: {}/New todo'.format('inbox'), r)

        s, r = New.run({'folder': 'today', 'action': 'New todo 2'})
        self.assertEqual(s, 'success')
        self.assertIn('Added: {}/New todo 2'.format('today'), r)

        s, r = New.run(
            {'folder': 'to', 'action': 'Sub item',
             'parent': {'folder': 'in', 'keywords': ['New', 'todo']}})
        self.assertEqual(s, 'success')
        self.assertIn('Added: {}/Sub item [New todo]'.format('today'), r)

    def test_new_item_saves_todo(self):
        New.run({'action': 'Todo 1'})
        New.run({'folder': 'today', 'action': 'Todo 2'})
        New.run({'folder': 'done', 'action': 'Todo 3'})
        New.run({'folder': 'someday', 'action': 'Todo 4'})
        todos = Todo.select()
        self.assertEqual(len(todos), 4)

    def test_new_item_saves_to_inbox_by_default(self):
        New.run({'action': 'Todo 1'})
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder.name, 'inbox')

    def test_new_item_saves_to_specified_folder(self):
        New.run({'folder': 't', 'action': 'Todo 1'})
        New.run({'folder': 'do', 'action': 'Todo 2'})
        New.run({'folder': 'some', 'action': 'Todo 3'})
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder.name, 'today')
        t2 = Todo.get(Todo.action == 'Todo 2')
        self.assertEqual(t2.folder.name, 'done')
        t3 = Todo.get(Todo.action == 'Todo 3')
        self.assertEqual(t3.folder.name, 'someday')

    @skip
    def test_new_item_saves_due_date(self):
        one_week = date.today() + timedelta(weeks=1)
        New.run(['Todo 1', 'due+1w'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.due, one_week)

    def test_new_item_saves_parent(self):
        project = Todo.create(action='Project')
        New.run({'action': 'Test todo',
                 'parent': {'folder': '', 'keywords': ['Project']}})
        t1 = Todo.get(Todo.action == 'Test todo')
        self.assertEqual(t1.parent, project)

    def test_should_return_error_when_saving_to_nonexisting_folder(self):
        s, r = New.run({'folder': 'nonfolder', 'action': 'New todo'})
        self.assertEqual(s, 'error')
        s, r = New.run({'folder': 'nonfolder', 'action': ''})
        self.assertEqual(s, 'error')

    def test_should_push_transaction_to_UndoStack(self):
        todo_info = {'folder': 'today', 'action': 'New todo'}
        New.run(todo_info)
        self.assertEqual(len(UndoStack.select()), 1)

    def test_transaction_should_encode_new_todo(self):
        todo_info = {'folder': 'today', 'action': 'New todo'}
        New.run(todo_info)
        transaction = UndoStack.pop()
        self.assertEqual(transaction.command, 'new')
        for k, v in todo_info.items():
            self.assertEqual(transaction.args[k], v)

    def test_new_transaction_should_record_timestamp(self):
        todo_info = {'folder': 'today', 'action': 'New todo'}
        New.run(todo_info)
        now = datetime.datetime.now()
        transaction = UndoStack.pop()
        timediff = (now - transaction.timestamp).total_seconds()
        self.assertAlmostEqual(timediff, 0, delta=0.01)
