from unittest import TestCase
from unittest.mock import Mock, patch

from todone import config
from todone.application import main
from todone.commands.dispatch import CommandDispatcher, dispatch_command
from todone.tests.base import ResetSettings
from todone.textparser import ArgumentError, TextParser


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
