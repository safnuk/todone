from unittest import TestCase
from unittest.mock import Mock, patch

from todone.commands.dispatch import dispatch_command, CommandDispatcher
from todone.parser.textparser import ArgumentError, TextParser

mock_help = Mock()
MockCommandMap = {
    'test': Mock(side_effect=ArgumentError),
    'help': mock_help
}
MOCK_PARSED_DATA = {
    'command': 'command',
    'args': ['args'],
    'config': 'config.ini',
}


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

    @patch('todone.commands.dispatch.TextParser')
    def test_parse_args_calls_TextParser_parse(self, MockParser):
        testargs = ['foo', 'bar']
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock()
        cd = CommandDispatcher(testargs)
        cd.parse_args()
        mock_instance.parse.assert_called_once_with(testargs)

    @patch('todone.commands.dispatch.TextParser')
    @patch('todone.commands.dispatch.dispatch_command')
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

    @patch('todone.commands.dispatch.TextParser')
    @patch('todone.commands.dispatch.dispatch_command')
    def test_parse_args_with_ArgumentError_exits(
            self, mock_dispatch, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=ArgumentError)
        cd = CommandDispatcher(['garbage', 'args'])
        with self.assertRaises(SystemExit):
            cd.parse_args()


    @patch('todone.commands.dispatch.TextParser')
    @patch('todone.commands.dispatch.configure')
    def test_configure_with_config_flag_calls_config_with_passed_file(
            self, mock_configure, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
        cd = CommandDispatcher(['foo'])
        cd.configure()
        mock_configure.assert_called_once_with('config.ini')

    @patch('todone.commands.dispatch.TextParser')
    @patch('todone.commands.dispatch.dispatch_command')
    def test_dispatch_command_passes_command_and_remaining_args_to_dispatch(
        self, mock_dispatch, MockParser
    ):
        mock_instance = MockParser.return_value
        mock_instance.parsed_data = MOCK_PARSED_DATA
        cd = CommandDispatcher(['foo'])
        cd.dispatch_command()
        mock_dispatch.assert_called_once_with('command', ['args'])


class TestDispatchCommand(TestCase):

    @patch('todone.commands.dispatch.COMMAND_MAPPING')
    def test_passes_args_to_command_function(self, MockCommandMap):
        mock_command_function = Mock()
        MockCommandMap.__getitem__.return_value = mock_command_function
        action = 'test'
        args = ['arg1', 'arg2']
        dispatch_command(action, args)
        MockCommandMap.__getitem__.assert_called_once_with(action)
        mock_command_function.assert_called_once_with(args)

    @patch('todone.commands.dispatch.COMMAND_MAPPING', MockCommandMap)
    def test_prints_short_help_on_ArgumentError(self):
        dispatch_command('test', ['arg1', 'arg2'])
        mock_help.assert_called_once_with(['--short', 'test'])
