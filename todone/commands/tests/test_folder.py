from contextlib import redirect_stdout
import io
from unittest import TestCase

from todone.backends.db import Folder
from todone.commands.folder import folder_command, parse_args
from todone import config
from todone.tests.base import DB_Backend
from todone.parser.textparser import ArgumentError


class TestFolderCommand(DB_Backend):

    def test_new_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['new', 'test'])
        s = f.getvalue()
        self.assertIn('Added folder: {}'.format('test/'), s)

    def test_new_with_existing_folder_raises_ArgumentError(self):
        Folder.create(name='test')
        with self.assertRaises(ArgumentError):
            folder_command(['new', 'test'])

    def test_new_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['new'])

    def test_new_with_multiple_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['new', 'foo', 'bar'])

    def test_rename_to_existing_folder_raises_ArgumentError(self):
        Folder.create(name='test')
        Folder.create(name='foo')
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'test', 'foo'])

    def test_rename_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename'])

    def test_rename_raises_when_source_folder_does_not_match(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'test', 'foo'])

    def test_raises_when_rename_with_one_folder(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'today'])

    def test_raises_when_rename_with_three_folders(self):
        with self.assertRaises(ArgumentError):
            folder_command(['rename', 'today', 'foo', 'bar'])

    def test_delete_with_no_folders_raises(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete'])

    def test_rename_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['rename', 'today', 'foo'])
        s = f.getvalue()
        self.assertIn('Renamed folder: {} -> {}'.format('today/', 'foo/'), s)

    def test_delete_raises_when_folder_does_not_match(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete', 'foo'])

    def test_delete_raises_when_more_than_one_folder_passed(self):
        with self.assertRaises(ArgumentError):
            folder_command(['delete', 'today', 'foo'])

    def test_delete_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            folder_command(['delete', 'today'])
        s = f.getvalue()
        self.assertIn('Deleted folder: {}'.format('today/'), s)

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
