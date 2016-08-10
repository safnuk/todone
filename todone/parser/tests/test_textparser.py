from unittest import TestCase
from unittest.mock import Mock, patch

from todone.parser.exceptions import ArgumentError
from todone.parser.format import (
    AbstractFormat,
    ApplyFunctionFormat,
    DateFormat,
    PassthroughFormat,
)
from todone.parser.match import (
    AbstractMatch,
    AlwaysMatch,
    EqualityMatch,
    RegexMatch,
)
from todone.parser.textparser import (
    Argument,
    Nargs,
    TextParser,
)


class MockAlwaysMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        self.call_list = []
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        self.call_list.append((targets, args))
        return args[0], args[1:]


class MockFixedNumberMatch(AbstractMatch):
    def __init__(self, match_limit, *args, **kwargs):
        self.call_list = []
        self.match_limit = match_limit
        self.number_of_matches = 0
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        self.call_list.append((targets, args))
        if self.number_of_matches < self.match_limit:
            self.number_of_matches += 1
            return args[0], args[1:]
        return None, args


class MockAlternatingMatch(MockFixedNumberMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        self.call_list.append((targets, args))
        if (self.number_of_matches < self.match_limit
                and len(self.call_list) % 2 == 1):
            self.match_limit += 1
            return args[0], args[1:]
        return None, args


class TestArgumentFactory(TestCase):

    def test_default_matcher_is_EqualityMatch(self):
        parser = Argument.create(name='name', options=[])
        self.assertTrue(issubclass(type(parser), EqualityMatch))

    def test_default_formater_is_PassthroughFormat(self):
        parser = Argument.create(name='name', options=[])
        self.assertTrue(issubclass(type(parser), PassthroughFormat))

    def test_created_argument_saves_name(self):
        parser = Argument.create(name='test')
        self.assertTrue(parser.name, 'test')

    def test_created_argument_saves_options(self):
        options = ['foo', 'bar']
        parser = Argument.create(name='test', options=options)
        self.assertTrue(parser.options, options)

    def test_create_used_passed_match_class(self):
        parser = Argument.create(name='test', match=RegexMatch)
        self.assertTrue(issubclass(type(parser), RegexMatch))

    def test_create_uses_passed_format_class(self):
        def f(x):
            return [y.lower() for y in x]

        parser = Argument.create(
            name='test',
            format_function=f,
            format=ApplyFunctionFormat
        )
        self.assertTrue(issubclass(type(parser), ApplyFunctionFormat))
        self.assertEqual(parser.format_function, f)


class MockPassthroughFormat(PassthroughFormat):
    def __init__(self, *args, **kwargs):
        self.format_call_list = []
        super().__init__(*args, **kwargs)

    def format(self, values):
        self.format_call_list.append(values)
        super().format(values)


class TestTextParser(TestCase):

    def test_default_values(self):
        parser = TextParser()
        self.assertEqual(parser.arguments, [])
        self.assertEqual(parser.parsed_data, {})

    def test_add_argument_creates_an_argument(self):
        parser = TextParser()
        parser.add_argument('name')
        parser.add_argument('test')
        self.assertEqual(len(parser.arguments), 2)
        self.assertEqual(parser.arguments[0].name, 'name')
        self.assertTrue(issubclass(type(parser.arguments[0]), Argument))
        self.assertEqual(parser.arguments[1].name, 'test')

    @patch('todone.parser.textparser.Argument')
    def test_add_argument_passes_args_to_create(self, MockArgument):
        parser = TextParser()
        parser.add_argument('name', options=['foo', 'bar'],
                            nargs=2, match=AlwaysMatch,
                            format=DateFormat)
        MockArgument.create.assert_called_once_with(
            'name', options=['foo', 'bar'],
            nargs=2, match=AlwaysMatch,
            format=DateFormat
        )

    def test_parse_calls_parse_for_each_argument(self):
        args = ['foo', 'bar', 'baz']
        parser = TextParser()
        parser.arguments = [Mock(), Mock()]
        for mock in parser.arguments:
            mock.parse = Mock()
            mock.options = None
        parser.arguments[0].parse.return_value = (
            'key1', args[0:1], args[1:]
        )
        parser.arguments[1].parse.return_value = (
            'key2', args[1:], []
        )
        parser.parse(args)
        parser.arguments[0].parse.assert_called_once_with(args)
        parser.arguments[1].parse.assert_called_once_with(args[1:])

    def test_parse_saves_parsed_arguments(self):
        args = ['foo', 'bar', 'baz']
        parser = TextParser()
        parser.arguments = [Mock(), Mock()]
        for mock in parser.arguments:
            mock.parse = Mock()
            mock.options = None
        parser.arguments[0].parse.return_value = (
            'key1', args[0:1], args[1:]
        )
        parser.arguments[1].parse.return_value = (
            'key2', args[1:], []
        )
        parser.parse(args)
        self.assertEqual(parser.parsed_data['key1'], args[:1])
        self.assertEqual(parser.parsed_data['key2'], args[1:])
        self.assertEqual(len(parser.parsed_data), 2)

    def test_parse_raises_if_args_remaining(self):
        args = ['foo', 'bar', 'baz']
        parser = TextParser()
        parser.arguments = [Mock(), Mock()]
        for mock in parser.arguments:
            mock.parse = Mock()
            mock.options = None
        parser.arguments[0].parse.return_value = (
            None, None, args
        )
        parser.arguments[1].parse.return_value = (
            'key2', args[:2], args[2:]
        )
        with self.assertRaises(ArgumentError):
            parser.parse(args)


class TestArgument(TestCase):

    def test_default_values(self):
        parser = Argument(name='test')
        self.assertEqual(parser.name, 'test')
        self.assertEqual(parser.options, None)
        self.assertEqual(parser.positional, True)
        self.assertEqual(parser.default, [])
        self.assertTrue(issubclass(type(parser.nargs), Nargs))
        self.assertTrue(parser.nargs.min == parser.nargs.max == 1)
        self.assertTrue(issubclass(type(parser), AbstractMatch))
        self.assertTrue(issubclass(type(parser), AbstractFormat))

    def test_format_called_on_matched_args(self):
        parser = Argument.create(
            name='name', nargs=2, match_limit=2,
            match=MockFixedNumberMatch,
            format=MockPassthroughFormat
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        parser.parse(args)
        self.assertEqual(parser.format_call_list, [
            ['foo', 'bar']
        ])

    def test_default_value_returned_when_no_match_found(self):
        parser = Argument.create(
            name='name', nargs='?', match_limit=0,
            match=MockFixedNumberMatch, default='default'
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, unmatched_args = parser.parse(args)
        self.assertEqual(value, 'default')

    def test_raises_when_not_enough_matches_with_integer_nargs(self):
        for n in range(2):
            parser = Argument.create(
                name='name', nargs=n+1, match_limit=n,
                match=MockFixedNumberMatch
            )
            args = ['foo', 'bar', 'buzz', 'baz']
            with self.assertRaises(ArgumentError):
                parser.parse(args)

    def test_raises_with_zero_matches_and_nargs_plus(self):
        parser = Argument.create(
            name='name', nargs='+', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        with self.assertRaises(ArgumentError):
            parser.parse(args)

    def test_does_not_raise_with_zero_matches_and_nargs_star(self):
        parser = Argument.create(
            name='name', nargs='*', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        parser.parse(args)  # does not raise

    def test_does_not_raise_with_zero_matches_and_nargs_question_mark(self):
        parser = Argument.create(
            name='name', nargs='?', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        parser.parse(args)  # does not raise


class TestPositionalArgument(TestCase):

    def test_parse_arg_stops_on_first_nonmatch(self):
        parser = Argument.create(
            name='name', positional=True, nargs='*', match_limit=2,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args[0:]),
            (None, args[1:]),
            (None, args[2:]),
        ])

    def test_parse_arg_stops_when_target_number_of_matches_found(self):
        for n in range(1, 4):
            parser = Argument.create(
                name='name', positional=True,
                nargs=n,
                match=MockAlwaysMatch)
            args = ['foo', 'bar', 'buzz', 'baz']
            key, value, unmatched_args = parser.parse(args)
            calls = n
            self.assertEqual(len(parser.call_list), calls)
            self.assertEqual(value, args[:n])
            self.assertEqual(unmatched_args, args[n:])

    def test_parse_arg_returns_key_and_empty_string_when_no_match(self):
        parser = Argument.create(
            name='name', positional=True, nargs='?', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args[0:]),
        ])
        self.assertEqual(key, 'name')
        self.assertEqual(value, [])
        self.assertEqual(remaining_args, args)


class TestNonPositionalArgument(TestCase):

    def test_parse_arg_calls_match_on_each_arg_when_nargs_multiple(self):
        parser = Argument.create(name='name', positional=False,
                                 nargs='+', match=MockAlwaysMatch)
        args = ['arg1', 'arg2', 'arg3']
        parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args),
            (None, args[1:]),
            (None, args[2:]),
        ])

    def test_parse_arg_does_not_stop_on_nonmatch(self):
        parser = Argument.create(
            name='name', positional=False, nargs='*', match_limit=2,
            match=MockAlternatingMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args[0:]),
            (None, args[1:]),
            (None, args[2:]),
            (None, args[3:]),
        ])
        self.assertEqual(key, 'name')

    def test_parse_arg_returns_matched_args(self):
        parser = Argument.create(
            name='name', positional=False, nargs=2, match_limit=2,
            match=MockAlternatingMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(value, ['foo', 'buzz'])

    def test_parse_arg_returns_unmatched_args(self):
        parser = Argument.create(
            name='name', positional=False, nargs=2, match_limit=2,
            match=MockAlternatingMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(remaining_args, ['bar', 'baz'])

    def test_parse_arg_stops_when_target_number_of_matches_found(self):
        for n in range(1, 7):
            parser = Argument.create(
                name='name', positional=False,
                nargs=n, match_limit=10,
                match=MockAlternatingMatch)
            args = [x for x in range(12)]
            evens = [x for x in args if x % 2 == 0]
            odds = [x for x in args if x % 2 == 1]
            key, value, unmatched_args = parser.parse(args)
            calls = 2*n - 1
            self.assertEqual(
                len(parser.call_list), calls,
                "Failed with call list = {}".format(parser.call_list))
            self.assertEqual(value, evens[:n])
            self.assertEqual(unmatched_args, odds[:n] + args[2*n:])

    def test_parse_arg_returns_key_and_empty_string_when_no_match(self):
        parser = Argument.create(
            name='name', positional=False, nargs='?', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args[0:]),
            (None, args[1:]),
            (None, args[2:]),
            (None, args[3:]),
        ])
        self.assertEqual(key, 'name')
        self.assertEqual(value, [])
        self.assertEqual(remaining_args, args)


class TestNargs(TestCase):

    def test_init_with_integer(self):
        for n in range(10):
            nargs = Nargs(n)
            self.assertEqual(nargs.min, n)
            self.assertEqual(nargs.max, n)

    def test_init_with_plus(self):
        nargs = Nargs('+')
        self.assertEqual(nargs.min, 1)
        self.assertEqual(nargs.max, float('inf'))

    def test_init_with_star(self):
        nargs = Nargs('*')
        self.assertEqual(nargs.min, 0)
        self.assertEqual(nargs.max, float('inf'))

    def test_init_with_question_mark(self):
        nargs = Nargs('?')
        self.assertEqual(nargs.min, 0)
        self.assertEqual(nargs.max, 1)
