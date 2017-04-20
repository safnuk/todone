from todone.backend import DEFAULT_FOLDERS
from todone.backend import db
import todone.backend.commands as cmd
from todone.tests.base import DB_Backend


class TestFolderCommand(DB_Backend):

    def test_new_outputs_action_taken(self):
        s, r = cmd.Folder.run({'subcommand': 'new', 'folders': ['test']})
        self.assertEqual(s, 'success')
        self.assertIn('Added folder: {}'.format('test/'), r)

    def test_new_with_existing_folder_should_return_error(self):
        db.Folder.create(name='test')
        s, r = cmd.Folder.run({'subcommand': 'new', 'folders': ['test']})
        self.assertEqual(s, 'error')

    def test_new_with_no_folders_should_return_error(self):
        s, r = cmd.Folder.run({'subcommand': 'new'})
        self.assertEqual(s, 'error')

    def test_new_with_multiple_folders_should_return_error(self):
        s, r = cmd.Folder.run({'subcommand': 'new', 'folders': ['foo', 'bar']})
        self.assertEqual(s, 'error')

    def test_rename_to_existing_folder_should_return_error(self):
        db.Folder.create(name='test')
        db.Folder.create(name='foo')
        s, r = cmd.Folder.run(
            {'subcommand': 'rename', 'folders': ['test', 'foo']})
        self.assertEqual(s, 'error')

    def test_rename_with_no_folders_should_return_error(self):
        s, r = cmd.Folder.run({'subcommand': 'rename'})
        self.assertEqual(s, 'error')

    def test_rename_should_error_when_source_folder_does_not_match(self):
        s, r = cmd.Folder.run(
            {'subcommand': 'rename', 'folders': ['test', 'foo']})
        self.assertEqual(s, 'error')

    def test_return_error_when_rename_with_one_folder(self):
        s, r = cmd.Folder.run({'subcommand': 'rename', 'folders': ['today']})
        self.assertEqual(s, 'error')

    def test_return_error_when_rename_with_three_folders(self):
        s, r = cmd.Folder.run({'subcommand': 'rename',
                               'folders': ['today', 'foo', 'bar']})
        self.assertEqual(s, 'error')

    def test_delete_with_no_folders_should_return_error(self):
        s, r = cmd.Folder.run({'subcommand': 'delete'})
        self.assertEqual(s, 'error')

    def test_rename_returns_action_taken(self):
        s, r = cmd.Folder.run({'subcommand': 'rename',
                               'folders': ['today', 'foo']})
        self.assertIn('Renamed folder: {} -> {}'.format('today/', 'foo/'), r)
        self.assertEqual(s, 'success')

    def test_delete_return_error_when_folder_does_not_match(self):
        s, r = cmd.Folder.run({'subcommand': 'delete', 'folders': ['foo']})
        self.assertEqual(s, 'error')

    def test_delete_should_return_error_when_more_than_one_folder_passed(self):
        s, r = cmd.Folder.run({'subcommand': 'delete',
                               'folders': ['today', 'foo']})
        self.assertEqual(s, 'error')

    def test_delete_returns_action_taken(self):
        s, r = cmd.Folder.run({'subcommand': 'delete', 'folders': ['today']})
        self.assertEqual(s, 'success')
        self.assertIn('Deleted folder: {}'.format('today/'), r)

    def test_list_returns_all_folders(self):
        s, r = cmd.Folder.run({'subcommand': 'list'})
        self.assertEqual(s, 'folder_query')
        for folder in DEFAULT_FOLDERS['folders']:
            self.assertIn(folder + '/', r)

    def test_list_should_return_error_with_extra_arguments(self):
        s, r = cmd.Folder.run({'subcommand': 'list', 'folders': ['foo']})
        self.assertEqual(s, 'error')
