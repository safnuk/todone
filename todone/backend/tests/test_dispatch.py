from unittest import TestCase
from unittest.mock import Mock, patch

from todone.backend.dispatch import dispatch_command
import todone.exceptions as exceptions

mock_help = Mock()
MockCommandMap = {
    'test': Mock(side_effect=exceptions.ArgumentError),
    'help': mock_help
}


class TestDispatchCommands(TestCase):

    @patch('todone.backend.dispatch.COMMAND_MAPPING')
    def test_passes_args_to_command_function(self, MockCommandMap):
        mock_command_function = Mock()
        MockCommandMap.__getitem__.return_value = mock_command_function
        action = 'test'
        args = {'arg1': 'arg1', 'arg2': 'arg2'}
        dispatch_command(action, args)
        MockCommandMap.__getitem__.assert_called_once_with(action)
        mock_command_function.assert_called_once_with(args)

    @patch('todone.backend.dispatch.COMMAND_MAPPING', MockCommandMap)
    def test_prints_short_help_on_ArgumentError(self):
        dispatch_command('test', {'arg1': 'arg1'})
        mock_help.assert_called_once()
