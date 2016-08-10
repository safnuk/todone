from unittest import TestCase
from unittest.mock import patch

from todone import config
from todone.application import main
from todone.tests.base import ResetSettings


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
