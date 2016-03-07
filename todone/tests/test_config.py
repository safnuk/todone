import os
from unittest import TestCase
from unittest.mock import patch

from todone.config import configure, settings


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


class IntegratedTestConfig(TestCase):

    def test_configure_updates_settings(self):
        test_settings = {'foo': 'bar', 'baz': 'biff'}
        name = settings['database']['name']
        configure('tests/test.ini')
        self.assertEqual(settings['test'], test_settings)
        self.assertEqual(settings['database']['type'], 'testing')
        self.assertEqual(settings['database']['name'], name)

    def test_configure_converts_comma_delineated_strings_to_lists(self):
        configure('tests/test.ini')
        self.assertEqual(settings['folders']['active'], ['foo', 'bar', 'baz'])
        self.assertEqual(settings['folders']['cal'], ['my_cal'])
