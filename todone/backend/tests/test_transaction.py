import datetime
import unittest

from todone.backend import transaction


class TestTransaction(unittest.TestCase):
    def test_new_transaction_should_have_timestamp(self):
        now = datetime.datetime.now()
        trans = transaction.Transaction('new', {'test': 'foo'})
        timediff = (now - trans.timestamp).total_seconds()
        self.assertAlmostEqual(timediff, 0, delta=0.01)

    def test_new_command_inverse_should_be_remove(self):
        trans = transaction.Transaction('new', {'id': 1, 'folder': 'inbox'})
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'remove')
        self.assertEqual(args['id'], trans.args['id'])
        self.assertEqual(args['folder'], 'inbox')

    def test_remove_command_inverse_should_be_new(self):
        trans = transaction.Transaction('remove', {'id': 1, 'folder': 'inbox'})
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'new')
        self.assertEqual(args['id'], trans.args['id'])
        self.assertEqual(args['folder'], 'inbox')

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
        trans1 = {'todo': 1, 'old_folder': 'inbox', 'new_folder': 'foo'}
        trans = transaction.Transaction(
            'folder', {'subcommand': 'new', 'folders': ['foo'],
                       'todos': [trans1]}
        )
        inverse = trans.inverse()
        args = inverse.args
        todos = args['todos'][0]
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'delete')
        self.assertEqual(args['folders'], trans.args['folders'])
        self.assertEqual(todos['old_folder'], 'foo')
        self.assertEqual(todos['new_folder'], 'inbox')

    def test_inverse_of_delete_folder_should_be_new(self):
        trans1 = {'todo': 1, 'old_folder': 'foo', 'new_folder': 'inbox'}
        trans = transaction.Transaction(
            'folder',
            {'subcommand': 'delete', 'folders': ['foo'], 'todos': [trans1]}
        )
        inverse = trans.inverse()
        args = inverse.args
        todos = args['todos'][0]
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'new')
        self.assertEqual(args['folders'], trans.args['folders'])
        self.assertEqual(todos['old_folder'], 'inbox')
        self.assertEqual(todos['new_folder'], 'foo')

    def test_inverse_of_folder_rename_should_swap_folders(self):
        trans = transaction.Transaction(
            'folder', {'subcommand': 'rename',
                       'folders': ['foo', 'bar']}
        )
        inverse = trans.inverse()
        args = inverse.args
        self.assertEqual(inverse.command, 'folder')
        self.assertEqual(args['subcommand'], 'rename')
        self.assertEqual(args['folders'], ['bar', 'foo'])
