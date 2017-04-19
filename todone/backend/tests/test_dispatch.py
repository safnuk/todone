from unittest import TestCase
from unittest.mock import call, Mock, patch

from todone.commands.dispatch import dispatch_command
import todone.exceptions as exceptions

mock_help = Mock()
MockCommandMap = {
    'test': Mock(side_effect=exceptions.ArgumentError),
    'help': mock_help
}


class TestDispatchCommand(TestCase):

    @patch('todone.commands.dispatch.COMMAND_MAPPING')
    def test_passes_args_to_command_function(self, MockCommandMap):
        mock_command_function = Mock()
        MockCommandMap.__getitem__.return_value = mock_command_function
        action = {'command': 'test'}
        args = {'arg1': 'arg1', 'arg2': 'arg2'}
        dispatch_command([action.update(args)])
        MockCommandMap.__getitem__.assert_called_once_with(action['command'])
        mock_command_function.assert_called_once_with(args)

    @patch('todone.commands.dispatch.COMMAND_MAPPING')
    def test_processes_multiple_commands(self, MockCommandMap):
        mock_command_function = Mock()
        MockCommandMap.__getitem__.return_value = mock_command_function
        action = {'command': 'test'}
        args = {'arg1': 'arg1', 'arg2': 'arg2'}
        dispatch_command([action.update(args)] * 2)
        dispatch_calls = [call(action['command'])] * 2
        process_calls = [call(args)]*2
        MockCommandMap.__getitem__.assert_has_calls(dispatch_calls)
        mock_command_function.assert_has_calls(process_calls)

    @patch('todone.commands.dispatch.COMMAND_MAPPING', MockCommandMap)
    def test_prints_short_help_on_ArgumentError(self):
        dispatch_command({'command': 'test', 'arg1': 'arg1'})
        mock_help.assert_called_once_with(['--short', 'test'])
