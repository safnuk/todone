from contextlib import redirect_stdout
import io

from todone.backend import DEFAULT_FOLDERS
from todone.backend import db
import todone.backend.commands as cmd
from todone.tests.base import DB_Backend
import todone.exceptions as exceptions


class TestFolderCommand(DB_Backend):

    def test_new_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Folder.run({'subcommand': 'new', 'folders': ['test']})
        s = f.getvalue()
        self.assertIn('Added folder: {}'.format('test/'), s)

    def test_new_with_existing_folder_raises_ArgumentError(self):
        db.Folder.create(name='test')
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'new', 'folders': ['test']})

    def test_new_with_no_folders_raises(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'new'})

    def test_new_with_multiple_folders_raises(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'new', 'folders': ['foo', 'bar']})

    def test_rename_to_existing_folder_raises_ArgumentError(self):
        db.Folder.create(name='test')
        db.Folder.create(name='foo')
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'rename', 'folders': ['test', 'foo']})

    def test_rename_with_no_folders_raises(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'rename'})

    def test_rename_raises_when_source_folder_does_not_match(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'rename', 'folders': ['test', 'foo']})

    def test_raises_when_rename_with_one_folder(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'rename', 'folders': ['today']})

    def test_raises_when_rename_with_three_folders(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'rename',
                            'folders': ['today', 'foo', 'bar']})

    def test_delete_with_no_folders_raises(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'delete'})

    def test_rename_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Folder.run({'subcommand': 'rename',
                            'folders': ['today', 'foo']})
        s = f.getvalue()
        self.assertIn('Renamed folder: {} -> {}'.format('today/', 'foo/'), s)

    def test_delete_raises_when_folder_does_not_match(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'delete', 'folders': ['foo']})

    def test_delete_raises_when_more_than_one_folder_passed(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'delete',
                            'folders': ['today', 'foo']})

    def test_delete_outputs_action_taken(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Folder.run({'subcommand': 'delete', 'folders': ['today']})
        s = f.getvalue()
        self.assertIn('Deleted folder: {}'.format('today/'), s)

    def test_list_displays_all_folders(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Folder.run({'subcommand': 'list'})
        s = f.getvalue()
        for folder in DEFAULT_FOLDERS['folders']:
            self.assertIn(folder, s)

    def test_list_raises_with_extra_arguments(self):
        with self.assertRaises(exceptions.ArgumentError):
            cmd.Folder.run({'subcommand': 'list', 'folders': ['foo']})
