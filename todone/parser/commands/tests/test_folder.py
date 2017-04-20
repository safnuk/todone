from unittest import TestCase

from todone.parser.commands.folder import parse_args


class TestArgParse(TestCase):

    def test_parses_subcommands(self):
        args = parse_args(['new', 'test/'])
        self.assertEqual(args['subcommand'], 'new')
        args = parse_args(['n', 'test'])
        self.assertEqual(args['subcommand'], 'new')
        args = parse_args(['Rename', 'test'])
        self.assertEqual(args['subcommand'], 'rename')
        args = parse_args(['DEL', 'test'])
        self.assertEqual(args['subcommand'], 'delete')

    def test_parses_folder(self):
        args = parse_args(['n', 'test'])
        self.assertEqual(args['folders'], ['test', ])

    def test_parses_multiple_folders(self):
        args = parse_args(['n', 'test', 'foo', 'bar'])
        self.assertEqual(args['folders'], ['test', 'foo', 'bar'])

    def test_strips_trailing_slash_from_folders(self):
        args = parse_args(['n', 'test/'])
        self.assertEqual(args['folders'], ['test', ])
