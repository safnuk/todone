from contextlib import redirect_stdout
import io
import sys
from unittest import TestCase
from unittest.mock import Mock, patch

from todone import config
from todone.application import main
from todone.tests.base import ResetSettings
from todone.textparser import ArgumentError

mock_parsed_data = {
    'command': 'command',
    'args': ['args'],
    'config': 'config.ini',
}


@patch('todone.application.configure')
@patch('todone.application.TextParser')
@patch('todone.backends.db.database')
class UnitTestMain(TestCase):

    def setUp(self):
        sys.argv = ['todone']

    @patch('todone.application.dispatch_command')
    def test_main_with_no_args_uses_system_args(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        sys.argv = ['todone', 'new', 'Todo']
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = mock_parsed_data
        main()
        mock_instance.parse.assert_called_once_with(['new', 'Todo'])

    @patch('todone.application.dispatch_command')
    def test_main_with_no_args_or_sys_args_gives_help(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = mock_parsed_data
        main()
        mock_instance.parse.assert_called_once_with(['help'])

    def test_main_with_invalid_args_displays_short_help_message(
        self, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=ArgumentError)
        f = io.StringIO()
        with redirect_stdout(f):
            try:
                main(['garbage', 'new'])
            except SystemExit:
                pass
        s = f.getvalue()
        mock_instance.parse.assert_called_once_with(['garbage', 'new'])
        self.assertIn('Invalid argument(s)', s)
        self.assertIn('usage:', s)

    @patch('todone.application.dispatch_command')
    def test_main_with_config_flag_calls_config_with_passed_file(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = mock_parsed_data
        main(['-c config.ini', 'command', 'args'])
        mock_configure.assert_called_once_with('config.ini')

    @patch('todone.application.dispatch_command')
    def test_main_passes_command_and_remaining_args_to_dispatch(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = mock_parsed_data
        main(['command', 'args'])
        mock_dispatch.assert_called_once_with('command', ['args'])


class IntegratedTestMain(ResetSettings, TestCase):

    @patch('todone.backends.db.database')
    def test_config_flag_passed_to_configure(self, mock_db):
        main(['-c', 'todone/tests/test.ini', 'help'])
        self.assertEqual(config.settings['test']['foo'], 'bar')

    @patch('todone.backends.db.database')
    def test_passed_config_overrides_default(self, mock_db):
        main(['-c', 'todone/tests/config_db.ini', 'help'])
        self.assertEqual(
            config.settings['database']['name'], 'todone/tests/test.sqlite3')
