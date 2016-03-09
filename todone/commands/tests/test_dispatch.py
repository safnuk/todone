from unittest import TestCase
from unittest.mock import Mock, patch

from todone.commands.dispatch import dispatch_command
from todone.textparser import ArgumentError

mock_help = Mock()
MockCommandMap = {
    'test': Mock(side_effect=ArgumentError),
    'help': mock_help
}


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
