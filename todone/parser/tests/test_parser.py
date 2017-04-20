from unittest import TestCase
from unittest.mock import Mock, patch

from hamcrest import assert_that, contains_string
import todone.parser.parser as parser
from todone.parser import exceptions as pe


class TestParser(TestCase):
    def setUp(self):
        self.mock_parsed_data = (
            'command', {'args': ['args'], 'config': 'config.ini', })

    def test_init_stores_passed_args(self):
        test_args = ['test', 'foo']
        cd = parser.Parser(test_args)
        self.assertEqual(cd.args, test_args)

    def test_init_with_empty_args_stores_sysargs(self):
        mock_argv = ['test', 'bar']
        with patch('sys.argv', mock_argv):
            cd = parser.Parser(None)
            self.assertEqual(cd.args, mock_argv[1:])

    def test_init_with_empty_args_and_sysargs_stores_DEFAULT(self):
        mock_argv = ['todone']
        with patch('sys.argv', mock_argv):
            cd = parser.Parser(None)
            self.assertEqual(cd.args, cd.DEFAULT_ARGS)

    @patch('todone.parser.parser.factory.ParserFactory.from_arg_list')
    def test_parsing_command_with_ArgumentError_returns_error_command(
            self, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=pe.ArgumentError)
        p = parser.Parser(['garbage', 'args'])
        cmds = p.commands
        cmd = cmds[0]
        self.assertEqual(cmd[0], 'error')

    @patch('todone.parser.parser.factory.ParserFactory.from_arg_list')
    def test_parsing_command_with_ArgumentError_returns_help_command(
            self, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=pe.ArgumentError)
        p = parser.Parser(['garbage', 'args'])
        cmds = p.commands
        cmd = cmds[1]
        self.assertEqual(cmd[0], 'help')

    def test_config_flag_parses_with_passed_file(self):
        p = parser.Parser(['-c', 'foo', 'help'])
        cmd = p.commands[0]
        self.assertEqual(cmd[0], 'configure')
        self.assertEqual(cmd[1]['file'], 'foo')

    def test_no_config_flag_parses_to_empty_config_file(self):
        p = parser.Parser(['help'])
        cmd = p.commands[0]
        self.assertEqual(cmd[0], 'configure')
        self.assertEqual(cmd[1]['file'], '')

    def test_parsed_command_added_to_command_list(self):
        p = parser.Parser(['help'])
        cmd, args = p.commands[1]
        self.assertEqual(cmd, 'help')
        self.assertFalse(args['subcommand'])

    @patch('todone.parser.parser.factory.ParserFactory.from_arg_list')
    def test_parsing_args_with_ArgumentError_returns_error_command(
            self, MockTextParser):
        mock_instance = MockTextParser.return_value
        mock_instance.parse = Mock(side_effect=pe.ArgumentError)
        p = parser.ArgParser('folder', ['garbage'])
        cmds = p.commands
        cmd = cmds[0]
        self.assertEqual(cmd[0], 'error')
        assert_that(cmd[1]['message'], contains_string('Invalid argument(s)'))

    @patch('todone.parser.parser.factory.ParserFactory.from_arg_list')
    def test_parsing_args_with_ArgumentError_returns_help_command(
            self, MockTextParser):
        mock_instance = MockTextParser.return_value
        mock_instance.parse = Mock(side_effect=pe.ArgumentError)
        p = parser.ArgParser('folder', ['garbage'])
        cmds = p.commands
        cmd = cmds[1]
        self.assertEqual(cmd[0], 'help')
        self.assertTrue(cmd[1]['short'])
        self.assertEqual(cmd[1]['subcommand'], 'folder')
