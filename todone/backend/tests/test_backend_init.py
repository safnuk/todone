from unittest import TestCase
from unittest.mock import patch

from todone.backend import Database, DatabaseError


class TestDatabase(TestCase):

    @patch('todone.backend.loader.config.settings')
    def test_database_connect_should_raise_with_missing_type(
        self, mock_settings
    ):
        mock_settings.__getitem__.return_value = {'name': ''}
        with self.assertRaises(DatabaseError):
            Database.connect()
