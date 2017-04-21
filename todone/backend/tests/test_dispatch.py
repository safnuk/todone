from unittest import TestCase
from unittest.mock import Mock, patch

from todone.backend.dispatch import dispatch_command
import todone.exceptions as exceptions

mock_help = Mock()
mock_test = Mock()
mock_test.run = Mock(side_effect=exceptions.ArgumentError)
mock_test2 = Mock()
mock_test2.run = Mock()

MockCommandMap = {
    'test': mock_test,
    'test2': mock_test2,
    'help': mock_help
}


class TestDispatchCommands(TestCase):

    @patch('todone.backend.dispatch.cmd.COMMAND_MAPPING', MockCommandMap)
    def test_passes_args_to_command_function(self):
        action = 'test2'
        args = {'arg1': 'arg1', 'arg2': 'arg2'}
        dispatch_command(action, args)
        mock_test2.run.assert_called_once_with(args)

    @patch('todone.backend.dispatch.cmd.COMMAND_MAPPING', MockCommandMap)
    def test_prints_short_help_on_ArgumentError(self):
        dispatch_command('test', {'arg1': 'arg1'})
        mock_help.run.assert_called_once()
