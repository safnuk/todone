from contextlib import redirect_stdout
import io
from unittest import TestCase
from unittest.mock import patch

from todone.commands.setup import setup_db, version
from todone.config import VERSION
from todone.textparser import ArgumentError


class TestVersion(TestCase):

    def test_version_prints_current_version(self):
        f = io.StringIO()
        with redirect_stdout(f):
            version([])
        s = f.getvalue()
        self.assertIn('Todone', s)
        self.assertIn(VERSION, s)

    def test_version_with_arguments_raises(self):
        with self.assertRaises(ArgumentError):
            version(['arg'])


@patch('todone.commands.setup.create_tables')
class TestSetup(TestCase):

    def test_setup_with_arguments_raises(self, mock_create_tables):
        with self.assertRaises(ArgumentError):
            setup_db(['arg'])
        mock_create_tables.assert_not_called()

    def test_setup_calls_create_tables_once(self, mock_create_tables):
        setup_db([])
        mock_create_tables.assert_called_once_with()
