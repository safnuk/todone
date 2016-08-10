from contextlib import redirect_stdout
import io
import sys
from unittest import TestCase
from unittest.mock import Mock, patch

from todone import config
from todone.application import main, CommandDispatcher
from todone.tests.base import ResetSettings
from todone.textparser import ArgumentError, TextParser

MOCK_PARSED_DATA = {
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
        mock_instance.parsed_data = MOCK_PARSED_DATA
        main()
        mock_instance.parse.assert_called_once_with(['new', 'Todo'])

    @patch('todone.application.dispatch_command')
    def test_main_with_no_args_or_sys_args_gives_help(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
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
        mock_instance.parsed_data = MOCK_PARSED_DATA
        main(['-c config.ini', 'command', 'args'])
        mock_configure.assert_called_once_with('config.ini')

    @patch('todone.application.dispatch_command')
    def test_main_passes_command_and_remaining_args_to_dispatch(
        self, mock_dispatch, mock_db, MockParser, mock_configure
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
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


class TestCommandDispatcher(TestCase):

    def test_class_can_init(self):
        cd = CommandDispatcher(None)
        self.assertEqual(type(cd), CommandDispatcher)

    def test_init_stores_passed_args(self):
        test_args = ['test', 'foo']
        cd = CommandDispatcher(test_args)
        self.assertEqual(cd.args, test_args)

    def test_init_with_empty_args_stores_sysargs(self):
        mock_argv = ['test', 'bar']
        with patch('sys.argv', mock_argv):
            cd = CommandDispatcher(None)
            self.assertEqual(cd.args, mock_argv[1:])

    def test_init_with_empty_args_and_sysargs_stores_DEFAULT(self):
        mock_argv = ['todone']
        with patch('sys.argv', mock_argv):
            cd = CommandDispatcher(None)
            self.assertEqual(cd.args, cd.DEFAULT_ARGS)

    def test_init_creates_parser(self):
        cd = CommandDispatcher(None)
        self.assertEqual(type(cd.parser), TextParser)

    @patch('todone.application.TextParser')
    def test_parse_args_calls_TextParser_parse(self, MockParser):
        testargs = ['foo', 'bar']
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock()
        cd = CommandDispatcher(testargs)
        cd.parse_args()
        mock_instance.parse.assert_called_once_with(testargs)

    @patch('todone.application.TextParser')
    @patch('todone.application.dispatch_command')
    def test_parse_args_with_ArgumentError_dispatches_help_command(
            self, mock_dispatch, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=ArgumentError)
        cd = CommandDispatcher(['garbage', 'args'])
        try:
            cd.parse_args()
        except SystemExit:
            pass
        mock_dispatch.assert_called_with('help', ['--short'])

    @patch('todone.application.TextParser')
    @patch('todone.application.dispatch_command')
    def test_parse_args_with_ArgumentError_exits(
            self, mock_dispatch, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=ArgumentError)
        cd = CommandDispatcher(['garbage', 'args'])
        with self.assertRaises(SystemExit):
            cd.parse_args()


    @patch('todone.application.TextParser')
    @patch('todone.application.configure')
    def test_configure_with_config_flag_calls_config_with_passed_file(
            self, mock_configure, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
        cd = CommandDispatcher(['foo'])
        cd.configure()
        mock_configure.assert_called_once_with('config.ini')

    @patch('todone.application.TextParser')
    @patch('todone.application.dispatch_command')
    def test_dispatch_command_passes_command_and_remaining_args_to_dispatch(
        self, mock_dispatch, MockParser
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
        cd = CommandDispatcher(['foo'])
        cd.dispatch_command()
        mock_dispatch.assert_called_once_with('command', ['args'])
