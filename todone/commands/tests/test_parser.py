from unittest import TestCase
from unittest.mock import Mock, patch

from todone.commands import parser
from todone.parser import exceptions as pe


class TestParser(TestCase):
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

    @patch('todone.commands.dispatch.factory.ParserFactory.from_arg_list')
    def test_get_commands_with_ArgumentError_returns_error_command(
            self, MockParser):
        mock_instance = MockParser.return_value
        mock_instance.parse = Mock(side_effect=pe.ArgumentError)
        p = parser.Parser(['garbage', 'args'])
        cmds = p.commands
        self.assertEqual(len(cmds), 1)
        cmd = cmds[0]
        self.assertEqual(cmd['command'], 'error')
        self.assertEqual(cmd['message'], 'Could not parse command')

    def test_config_flag_parses_with_passed_file(self):
        p = parser.Parser(['-c', 'foo'])
        cmd = p.commands[0]
        self.assertEqual(cmd['command'], 'configure')
        self.assertEqual(cmd['file'], 'foo')
