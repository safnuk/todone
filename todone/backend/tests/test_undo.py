from todone.backend import commands as cmd
from todone.backend import db
from todone.tests.base import DB_Backend


class TestUndo(DB_Backend):
    def test_undo_new_should_remove(self):
        cmd.New.run({'action': 'New todo'})
        cmd.Undo.run({})
        self.assertEqual(len(db.Todo.select()), 0)

    def test_undo_move_should_move_todo_back(self):
        cmd.New.run({'action': 'New todo'})
        cmd.List.run({'keywords': ['todo']})
        cmd.Move.run({'index': 1, 'folder': 'today'})
        cmd.Undo.run({})
        self.assertEqual(len(db.Todo.select().where(
            db.Todo.folder == 'inbox')), 1)


class TestRedo(DB_Backend):
    def test_redo_should_revert_undo(self):
        cmd.New.run({'action': 'New todo'})
        cmd.Undo.run({})
        cmd.Redo.run({})
        self.assertEqual(len(db.Todo.select().where(
            db.Todo.folder == 'inbox')), 1)
