from contextlib import redirect_stdout
import io
from unittest import TestCase
from unittest.mock import patch


from todone.backend import DatabaseError
from todone.commands.setup import setup_db, version
from todone import config, __version__
from todone.parser import exceptions as pe


class TestVersion(TestCase):

    def test_version_prints_current_version(self):
        f = io.StringIO()
        with redirect_stdout(f):
            version([])
        s = f.getvalue()
        self.assertIn('Todone', s)
        self.assertIn(__version__, s)

    def test_version_with_arguments_raises(self):
        with self.assertRaises(pe.ArgumentError):
            version(['arg'])


@patch('todone.commands.setup.config.save_configuration')
@patch('todone.commands.setup.backend.Database.create')
class TestSetup(TestCase):

    def test_setup_without_arguments_raises(
        self, mock_create_database, mock_save_configuration
    ):
        with self.assertRaises(pe.ArgumentError):
            setup_db([])
        mock_create_database.assert_not_called()

    def test_setup_with_subcommand_does_not_raise(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            setup_db(['init'])  # should not raise

    def test_setup_with_extra_args_raises(
        self, mock_create_database, mock_save_configuration
    ):
        with self.assertRaises(pe.ArgumentError):
            setup_db(['init', 'extra'])
        mock_create_database.assert_not_called()

    def test_setup_init_with_valid_config_calls_create_database_once(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            setup_db(['init'])
        mock_create_database.assert_called_once_with()

    def test_DatabaseError_for_existing_db_prints_db_exists_msg(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = DatabaseError(
                "Database already exists")
            f = io.StringIO()
            with redirect_stdout(f):
                setup_db(['init'])
            s = f.getvalue()
        self.assertNotIn('New todone database initialized', s)
        self.assertIn('Database has already been setup - get working!', s)

    def test_database_creation_error_should_raise(
        self, mock_create_database, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': 'nonempty'}}):
            mock_create_database.side_effect = DatabaseError(
                "Could not create the database")
            with self.assertRaises(DatabaseError):
                setup_db(['init'])


@patch('todone.commands.setup.config.save_configuration')
@patch('todone.commands.setup.backend.Database')
@patch('todone.commands.setup.Setup.get_input', return_value='test file')
class TestInitialize(TestCase):
    def test_blank_db_name_queries_creation_of_config_file(
        self, mock_input, MockDatabase, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': ''}}):
            setup_db(['init'])
            self.assertEquals(config.settings['database']['name'], 'test file')
            mock_save_configuration.assert_called_once_with()
            MockDatabase.create.assert_called_once_with()

    def test_blank_db_name_calls_Database_update(
        self, mock_input, MockDatabase, mock_save_configuration
    ):
        with patch.dict(config.settings, {'database': {'name': ''}}):
            setup_db(['init'])
            MockDatabase.update.assert_called_once()
