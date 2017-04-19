from contextlib import redirect_stdout
from datetime import date, timedelta
import io

from todone.backend.db import Todo
from todone.backend.commands.new import new_todo
from todone.tests.base import DB_Backend
import todone.exceptions as exceptions


class TestNewAction(DB_Backend):

    def test_new_item_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            new_todo(['New todo'])
        s = f.getvalue()
        self.assertIn('Added: {}/New todo'.format('inbox'), s)

        f = io.StringIO()
        with redirect_stdout(f):
            new_todo(['today/', 'New todo 2'])
        s = f.getvalue()
        self.assertIn('Added: {}/New todo 2'.format('today'), s)

        f = io.StringIO()
        with redirect_stdout(f):
            new_todo(['to/', 'Sub item', '[in/New todo]'])
        s = f.getvalue()
        self.assertIn('Added: {}/Sub item [New todo]'.format('today'), s)

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
        new_todo(['TODAY/Todo 1'])
        new_todo(['Do/Todo 2'])
        new_todo(['some/Todo 3'])
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

    def test_new_item_saves_parent(self):
        project = Todo.create(action='Project')
        new_todo(['Test todo', '[Project]'])
        t1 = Todo.get(Todo.action == 'Test todo')
        self.assertEqual(t1.parent, project)

    def test_raises_ArgumentError_when_saving_to_nonexisting_folder(self):
        with self.assertRaises(exceptions.ArgumentError):
            new_todo(['nonfolder/', 'New todo'])
        with self.assertRaises(exceptions.ArgumentError):
            new_todo(['nonfolder/'])