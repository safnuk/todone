from contextlib import redirect_stdout
import io
from unittest import TestCase
from unittest.mock import patch

import peewee

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


@patch('todone.commands.setup.create_database')
class TestSetup(TestCase):

    def test_setup_with_arguments_raises(self, mock_create_database):
        with self.assertRaises(ArgumentError):
            setup_db(['arg'])
        mock_create_database.assert_not_called()

    def test_setup_calls_create_database_once(self, mock_create_database):
        setup_db([])
        mock_create_database.assert_called_once_with()

    def test_peewee_Exception_prints_db_exists_msg(self, mock_create_database):
        mock_create_database.side_effect = peewee.OperationalError
        f = io.StringIO()
        with redirect_stdout(f):
            setup_db([])
        s = f.getvalue()
        self.assertNotIn('New todone database initialized', s)
        self.assertIn('Database has already been setup - get working!', s)
