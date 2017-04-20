from unittest import TestCase
from unittest.mock import patch


from todone.backend.commands import Setup, Version
from todone import config, __version__
import todone.exceptions as exceptions


class TestVersion(TestCase):

    def test_version_should_output_current_version(self):
        s, r = Version.run({})
        self.assertEqual(s, 'success')
        self.assertIn('Todone', r)
        self.assertIn(__version__, r)


@patch('todone.backend.commands.config.save_configuration')
@patch('todone.backend.commands.backend.Database.create')
class TestSetup(TestCase):
    def test_setup_init_with_valid_config_calls_create_database_once(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            Setup.run({'subcommand': 'init'})
        mock_create_database.assert_called_once_with()

    def test_DatabaseError_for_existing_db_should_return_message(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = exceptions.DatabaseError(
                "Database already exists")
            s, r = Setup.run({'subcommand': 'init'})
        self.assertEqual(s, 'success')
        self.assertNotIn('New todone database initialized', r)
        self.assertIn('Database has already been setup - get working!', r)

    def test_database_creation_error_should_return_error(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = exceptions.DatabaseError(
                "Could not create the database")
            s, r = Setup.run({'subcommand': 'init'})
            self.assertEqual(s, 'error')


@patch('todone.backend.commands.config.save_configuration')
@patch('todone.backend.commands.backend.Database')
@patch('todone.backend.commands.Setup.get_input', return_value='test file')
class TestInitialize(TestCase):
    def test_blank_db_name_queries_creation_of_config_file(
        self, mock_input, MockDatabase, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': ''}}):
            Setup.run({'subcommand': 'init'})
            self.assertEquals(config.settings['database']['name'], 'test file')
            mock_save_configuration.assert_called_once_with()
            MockDatabase.create.assert_called_once_with()

    def test_blank_db_name_calls_Database_update(
        self, mock_input, MockDatabase, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': ''}}):
            Setup.run({'subcommand': 'init'})
            MockDatabase.update.assert_called_once()
