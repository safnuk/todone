import os
from unittest import TestCase
from unittest.mock import patch

from todone import config
from todone.config import configure
from todone.tests.base import ResetSettings


@patch('configparser.ConfigParser')
class UnitTestConfig(TestCase):

    def test_configure_with_blank_file_loads_default_ini(self, MockConfig):
        default_config = os.environ.get('HOME')
        default_config += '/.config/todone/config.ini'
        configure('')
        MockConfig.return_value.read.assert_called_once_with(
            default_config
        )

    def test_configure_reads_passed_filename(self, MockConfig):
        configure('test.ini')
        MockConfig.return_value.read.assert_called_once_with('test.ini')


class IntegratedTestConfig(ResetSettings, TestCase):

    def test_configure_updates_settings(self):
        test_settings = {'foo': 'bar', 'baz': 'biff'}
        name = config.settings['database']['name']
        configure('tests/test.ini')
        self.assertEqual(config.settings['test'], test_settings)
        self.assertEqual(config.settings['database']['type'], 'testing')
        self.assertEqual(config.settings['database']['name'], name)

    def test_configure_converts_comma_delineated_strings_to_lists(self):
        configure('tests/test.ini')
        self.assertEqual(
            config.settings['folders']['active'], ['foo', 'bar', 'baz'])
        self.assertEqual(config.settings['folders']['cal'], ['my_cal'])
