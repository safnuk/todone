from unittest import TestCase

from todone.parser.commands.done import parse_args
import todone.exceptions as exceptions


class TestDoneArgParse(TestCase):

    def test_parses_integer(self):
        args = parse_args(['5'])
        self.assertEqual(args['index'], 5)

    def test_negative_integer_does_not_match(self):
        with self.assertRaises(exceptions.ArgumentError):
            parse_args(['-5'])

    def test_rejects_noninteger_index(self):
        with self.assertRaises(exceptions.ArgumentError):
            parse_args(['test'])

    def test_rejects_two_args(self):
        with self.assertRaises(exceptions.ArgumentError):
            parse_args(['1', '2'])
        with self.assertRaises(exceptions.ArgumentError):
            parse_args(['1', 'test'])
