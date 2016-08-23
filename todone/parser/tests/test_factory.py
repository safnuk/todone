from unittest import TestCase

from todone.parser.factory import (
    ParserFactory,
    PresetArgument,
)
from todone.parser.match import AlwaysMatch
from todone.parser.textparser import TextParser


class TestParserFactory(TestCase):
    def test_class_can_be_instantiated(self):
        ParserFactory()

    def test_factory_creates_parser(self):
        parser = ParserFactory.from_arg_list()
        self.assertEqual(type(parser), TextParser)

    def test_factory_creates_parser_without_arguments(self):
        parser = ParserFactory.from_arg_list()
        self.assertEqual(len(parser.arguments), 0)

    def test_factory_creates_parser_with_argument(self):
        parser = ParserFactory.from_arg_list(
            [(PresetArgument.all_remaining, {'name': 'test'}), ])
        self.assertEqual(len(parser.arguments), 1)

    def test_factory_creates_parser_with_arguments(self):
        arglist = [
            (PresetArgument.all_remaining, {'name': 'foo'}),
            (PresetArgument.all_remaining, {'name': 'bar'}),
        ]
        parser = ParserFactory.from_arg_list(arglist)
        self.assertEqual(len(parser.arguments), len(arglist))

    def test_factory_creates_specified_types_of_arguments(self):
        arglist = [
            (PresetArgument.all_remaining,
             {'name': 'foo'}),
        ]
        parser = ParserFactory.from_arg_list(arglist)
        arg = parser.arguments[0]
        self.assertEqual(arg.name, 'foo')
        self.assertTrue(issubclass(type(arg), AlwaysMatch))

    def test_factory_can_create_all_presets(self):
        args = [(arg, {'name': 'foo'}) for arg in PresetArgument]
        ParserFactory.from_arg_list(args)

    def test_factory_can_override_presets(self):
        arglist = [
            (PresetArgument.index,
             {'name': 'foo',
              'options': ['bar', 'baz'],
              'match': AlwaysMatch}
             ),
        ]
        parser = ParserFactory.from_arg_list(arglist)
        arg = parser.arguments[0]
        self.assertEqual(arg.options, ['bar', 'baz'])
        self.assertTrue(issubclass(type(arg), AlwaysMatch))
