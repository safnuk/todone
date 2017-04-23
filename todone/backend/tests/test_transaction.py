import datetime
import unittest

from todone.backend import db
from todone.backend import transaction


class TestTransaction(unittest.TestCase):
    def test_new_transaction_should_have_timestamp(self):
        now = datetime.datetime.now()
        trans = transaction.Transaction('new', {'test': 'foo'})
        timediff = (now - trans.timestamp).total_seconds()
        self.assertAlmostEqual(timediff, 0, delta=0.01)

    def test_new_command_invert_should_move_to_garbage(self):
        todo = db.Todo.create(action='New todo', folder='today')
        trans = transaction.Transaction('new', {'todo': todo.id})
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'move')
        self.assertEqual(args['todo'], trans.args['todo'])
        self.assertEqual(args['old_folder'], 'today')
        self.assertEqual(args['new_folder'], 'garbage')

    def test_move_folder_inverse_should_swap_folders(self):
        trans = transaction.Transaction(
            'move', {'todo': 1, 'old_folder': 'foo', 'new_folder': 'bar'})
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'move')
        self.assertEqual(args['todo'], trans.args['todo'])
        self.assertEqual(args['old_folder'], trans.args['new_folder'])
        self.assertEqual(args['new_folder'], trans.args['old_folder'])

    def test_move_parent_inverse_should_swap_parents(self):
        trans = transaction.Transaction(
            'move', {'todo': 1, 'old_parent': 1, 'new_parent': 2}
        )
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'move')
        self.assertEqual(args['todo'], trans.args['todo'])
        self.assertEqual(args['old_parent'], trans.args['new_parent'])
        self.assertEqual(args['new_parent'], trans.args['old_parent'])

    def test_inverse_of_new_folder_should_be_delete(self):
        trans = transaction.Transaction(
            'folder', {'subcommand': 'new', 'folder': 'foo'}
        )
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'delete')
        self.assertEqual(args['folder'], trans.args['folder'])

    def test_inverse_of_delete_folder_should_be_new(self):
        trans = transaction.Transaction(
            'folder',
            {'subcommand': 'delete', 'folder': 'foo', 'todos': [1, 2, 3]}
        )
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'new')
        self.assertEqual(args['folder'], trans.args['folder'])
        self.assertEquals(args['todos'], trans.args['todos'])

    def test_inverse_of_folder_rename_should_swap_folders(self):
        trans = transaction.Transaction(
            'folder', {'subcommand': 'rename',
                       'old_folder': 'foo', 'new_folder': 'bar'}
        )
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'rename')
        self.assertEqual(args['old_folder'], trans.args['new_folder'])
        self.assertEqual(args['new_folder'], trans.args['old_folder'])
