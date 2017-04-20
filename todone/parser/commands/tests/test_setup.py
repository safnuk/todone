from unittest import TestCase


from todone.parser.commands import setup
from todone.parser.commands import version
from todone.parser import exceptions as pe


class TestVersion(TestCase):
    def test_version_with_arguments_raises(self):
        with self.assertRaises(pe.ArgumentError):
            version.parse_args(['arg'])


class TestSetup(TestCase):

    def test_setup_without_arguments_raises(self):
        with self.assertRaises(pe.ArgumentError):
            setup.parse_args([])

    def test_setup_with_subcommand_does_not_raise(self):
            args = setup.parse_args(['init'])
            self.assertEqual(args, {'subcommand': 'init'})

    def test_invalid_subcommand_should_raise(self):
        with self.assertRaises(pe.ArgumentError):
            setup.parse_args(['garbage'])

    def test_setup_with_extra_args_raises(self):
        with self.assertRaises(pe.ArgumentError):
            setup.parse_args(['init', 'extra'])
