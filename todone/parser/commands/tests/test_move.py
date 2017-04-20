from unittest import TestCase

from todone.parser.commands.move import parse_args
from todone.parser import exceptions as pe


class TestMoveArgParse(TestCase):

    def test_parses_integer(self):
        args = parse_args(['5', 'today/'])
        self.assertEqual(args['index'], 5)

    def test_negative_integer_does_not_match(self):
        with self.assertRaises(pe.ArgumentError):
            parse_args(['-5', 'today/'])

    def test_parses_folder(self):
        args = parse_args(['0', 'inbox/'])
        self.assertEqual(args['folder'], 'inbox')

    def test_parses_parent(self):
        args = parse_args(['1', '[folder/project]'])
        self.assertEqual(
            args['parent'], {'folder': 'folder', 'keywords': ['project']}
        )

    def test_rejects_noninteger_index(self):
        with self.assertRaises(pe.ArgumentError):
            parse_args(['test'])
