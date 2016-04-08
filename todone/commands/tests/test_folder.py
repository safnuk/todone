from contextlib import redirect_stdout
import io
from unittest import TestCase

import peewee

from todone.backends.db import Folder, Todo
from todone.commands.folder import folder_command, parse_args
from todone import config
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

    def test_new_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['new'])

    def test_rename_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename'])

    def test_delete_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete'])

    def test_rename_changes_folder_name(self):
        Folder.create(name='test')
        folder_command(['rename', 'test', 'foo'])
        Folder.get(Folder.name == 'foo')  # does not raise
        with self.assertRaises(peewee.DoesNotExist):
            Folder.get(Folder.name == 'test')

    def test_rename_to_existing_folder_raises_ArgumentError(self):
        Folder.create(name='test')
        Folder.create(name='foo')
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'test', 'foo'])

    def test_rename_renames_folder_fields_for_todos(self):
        Folder.create(name='test')
        Todo.create(action='Todo 1', folder='test')
        folder_command(['rename', 'test', 'foo'])
        t1 = Todo.get(Todo.action == 'Todo 1')
        self.assertEqual(t1.folder.name, 'foo')

    def test_rename_raises_when_source_folder_does_not_match(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'test', 'foo'])

    def test_raises_when_rename_with_one_folder(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'today'])

    def test_raises_when_rename_with_three_folders(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'today', 'foo', 'bar'])

    def test_rename_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['rename', 'today', 'foo'])
        s = f.getvalue()
        self.assertIn('Renamed folder: {} -> {}'.format('today/', 'foo/'), s)

    def test_delete_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['delete', 'today'])
        s = f.getvalue()
        self.assertIn('Deleted folder: {}'.format('today/'), s)

    def test_delete_removes_folder(self):
        folder_command(['delete', 'today'])
        with self.assertRaises(peewee.DoesNotExist):
            Folder.get(name='today')

    def test_delete_moves_subtodos_to_default_inbox(self):
        Todo.create(action='Foo', folder='today')
        Todo.create(action='Bar', folder='today')
        folder_command(['delete', 'today'])
        for t in Todo.select():
            self.assertEqual(t.folder.name, 'inbox')

    def test_delete_raises_when_folder_does_not_match(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete', 'foo'])

    def test_delete_raises_when_more_than_one_folder_passed(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete', 'today', 'foo'])

    def test_list_displays_all_folders(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['list'])
        s = f.getvalue()
        for folder in config.settings['folders']['default_folders']:
            self.assertIn(folder, s)

    def test_list_raises_with_extra_arguments(self):
        with self.assertRaises(ArgumentError):
            folder_command(['list', 'foo'])


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

    def test_parses_folder(self):
        args = parse_args(['n', 'test'])
        self.assertEqual(args['folders'], ['test', ])

    def test_parses_multiple_folders(self):
        args = parse_args(['n', 'test', 'foo', 'bar'])
        self.assertEqual(args['folders'], ['test', 'foo', 'bar'])

    def test_strips_trailing_slash_from_folders(self):
        args = parse_args(['n', 'test/'])
        self.assertEqual(args['folders'], ['test', ])
