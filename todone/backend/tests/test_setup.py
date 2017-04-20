from contextlib import redirect_stdout
import io
from unittest import TestCase
from unittest.mock import patch


from todone.backend.commands import Setup, Version
from todone import config, __version__
import todone.exceptions as exceptions


class TestVersion(TestCase):

    def test_version_prints_current_version(self):
        f = io.StringIO()
        with redirect_stdout(f):
            Version.run({})
        s = f.getvalue()
        self.assertIn('Todone', s)
        self.assertIn(__version__, s)


@patch('todone.backend.commands.config.save_configuration')
@patch('todone.backend.commands.backend.Database.create')
class TestSetup(TestCase):
    def test_setup_init_with_valid_config_calls_create_database_once(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            Setup.run({'subcommand': 'init'})
        mock_create_database.assert_called_once_with()

    def test_DatabaseError_for_existing_db_prints_db_exists_msg(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = exceptions.DatabaseError(
                "Database already exists")
            f = io.StringIO()
            with redirect_stdout(f):
                Setup.run({'subcommand': 'init'})
            s = f.getvalue()
        self.assertNotIn('New todone database initialized', s)
        self.assertIn('Database has already been setup - get working!', s)

    def test_database_creation_error_should_raise(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = exceptions.DatabaseError(
                "Could not create the database")
            with self.assertRaises(exceptions.DatabaseError):
                Setup.run({'subcommand': 'init'})


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
