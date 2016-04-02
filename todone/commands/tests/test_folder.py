from contextlib import redirect_stdout
import io
from unittest import TestCase

from todone.backends.db import Folder
from todone.commands.folder import folder_command, parse_args
from todone.tests.base import DB_Backend
from todone.textparser import ArgumentError


class TestFolderCommand(DB_Backend):

    def test_new_creates_valid_name(self):
        old_list_length = len(Folder.select())
        folder_command(['new', 'test'])
        folder_command(['new', 'folder/'])
        self.assertEqual(len(Folder.select()) - old_list_length, 2)
        f1 = Folder.get(Folder.name == 'test')
        self.assertEqual(f1.name, 'test')
        f2 = Folder.get(Folder.name == 'folder')
        self.assertEqual(f2.name, 'folder')

    def test_new_with_existing_folder_raises_ArgumentError(self):
        Folder.create(name='test')
        with self.assertRaises(ArgumentError):
            folder_command(['new', 'test'])

    def test_new_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['new', 'test'])
        s = f.getvalue()
        self.assertIn('Added folder: {}'.format('test/'), s)
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['new', 'foo/', 'Bar'])
        s = f.getvalue()
        self.assertIn('Added folder: {}'.format('foo/'), s)
        self.assertIn('Added folder: {}'.format('Bar/'), s)

    def test_rename_changes_folder_name(self):
        return
        Folder.create(name='test')
        folder_command(['rename', 'test', 'foo'])
        Folder.get(Folder.name == 'foo')  # does not raise

    def test_rename_to_existing_folder_raises_ArgumentError(self):
        pass

    def test_rename_renames_folder_fields_for_todos(self):
        pass

    def test_raises_when_rename_with_one_folder(self):
        pass

    def test_raises_when_rename_with_three_folders(self):
        pass

    def test_delete_removes_folder(self):
        pass

    def test_delete_moves_subtodos_to_inbox(self):
        pass


class TestArgParse(TestCase):

    def test_parses_subcommands(self):
        args = parse_args(['new', 'test/'])
        self.assertEqual(args['command'], 'new')
        args = parse_args(['n', 'test'])
        self.assertEqual(args['command'], 'new')
        args = parse_args(['Rename', 'test'])
        self.assertEqual(args['command'], 'rename')
        args = parse_args(['DEL', 'test'])
        self.assertEqual(args['command'], 'delete')

    def test_raises_when_missing_folder(self):
        with self.assertRaises(ArgumentError):
            parse_args(['new'])

    def test_parses_folder(self):
        args = parse_args(['n', 'test'])
        self.assertEqual(args['folders'], ['test', ])

    def test_parses_multiple_folders(self):
        args = parse_args(['n', 'test', 'foo', 'bar'])
        self.assertEqual(args['folders'], ['test', 'foo', 'bar'])

    def test_strips_trailing_slash_from_folders(self):
        args = parse_args(['n', 'test/'])
        self.assertEqual(args['folders'], ['test', ])
