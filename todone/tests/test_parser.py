from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase
from unittest.mock import Mock, patch

from todone.textparser import (
    AbstractMatch,
    AbstractFormat,
    AlwaysMatch,
    ApplyFunctionFormat,
    Argument,
    ArgumentError,
    DateFormat,
    EqualityMatch,
    FolderMatch,
    Nargs,
    PassthroughFormat,
    RegexMatch,
    SubstringMatch,
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

    @patch('todone.textparser.Argument')
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
        parser.arguments[0].parse.assert_called_once_with(None, args)
        parser.arguments[1].parse.assert_called_once_with(None, args[1:])

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

    def test_parse_does_not_save_unmatched_arguments(self):
        args = ['foo', 'bar', 'baz']
        parser = TextParser()
        parser.arguments = [Mock(), Mock()]
        for mock in parser.arguments:
            mock.parse = Mock()
            mock.options = None
        parser.arguments[0].parse.return_value = (
            None, args[0:1], args[1:]
        )
        parser.arguments[1].parse.return_value = (
            'key2', args, []
        )
        parser.parse(args)
        with self.assertRaises(KeyError):
            type(parser.parsed_data['key1'])

        self.assertEqual(parser.parsed_data['key2'], args)
        self.assertEqual(len(parser.parsed_data), 1)

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

    def test_parse_arg_returns_null_key_when_no_match(self):
        parser = Argument.create(
            name='name', positional=True, nargs='?', match_limit=0,
            match=MockFixedNumberMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(parser.call_list, [
            (None, args[0:]),
        ])
        self.assertEqual(key, None)
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

    def test_parse_arg_returns_null_key_when_no_match(self):
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
        self.assertEqual(key, None)
        self.assertEqual(value, [])
        self.assertEqual(remaining_args, args)


class TestSubstringMatch(TestCase):

    def test_match_all_substrings(self):
        key = 'test'
        matcher = SubstringMatch()
        for n in range(1, len(key)):
            value, args = matcher.match([key], [key[:n], 'arg1', 'arg2'])
            self.assertEqual(value, key)

    def test_match_ignores_case(self):
        key = 'tESt'
        matcher = SubstringMatch()
        for n in range(1, len(key)):
            value, args = matcher.match(
                [key], [key[:n].lower(), 'arg1', 'arg2'])
            self.assertEqual(value, key)

            value, args = matcher.match(
                [key], [key[:n].upper(), 'arg1', 'arg2'])
            self.assertEqual(value, key)

    def test_match_tries_all_options(self):
        options = ['foo', 'bar', 'glob']
        matcher = SubstringMatch()
        for key in options:
            value, args = matcher.match(options, [key] + options)
            self.assertEqual(value, key)

    def test_match_only_unambiguous_substrings(self):
        options = ['foo', 'foa', 'fat']
        matcher = SubstringMatch()
        value, args = matcher.match(options, ['f'])
        self.assertEqual(value, None)
        value, args = matcher.match(options, ['fo'])
        self.assertEqual(value, None)
        value, args = matcher.match(options, ['foo'])
        self.assertEqual(value, 'foo')
        value, args = matcher.match(options, ['foa'])
        self.assertEqual(value, 'foa')
        value, args = matcher.match(options, ['fa'])
        self.assertEqual(value, 'fat')

    def test_match_strips_first_argument(self):
        matcher = SubstringMatch()
        value, args = matcher.match(['test'], ['test', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_no_match_does_not_strip_first_argument(self):
        matcher = SubstringMatch()
        value, args = matcher.match(['test'], ['arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])


class TestRegexMatch(TestCase):

    def test_regex_matches(self):
        options = [
            r'(due|du|d)\+(\d+)(d|w|m|y)',
            r'(due|du|d)',
        ]
        testargs = [
            ['due', 'test'],
            ['DU', 'test'],
            ['Due+5w'],
        ]
        matcher = RegexMatch()
        for testarg in testargs:
            value, args = matcher.match(options, testarg)
            self.assertEqual(value.string, testarg[0])

    def test_match_ignores_case(self):
        key = 'tESt'
        matcher = RegexMatch()
        value, args = matcher.match(
            [key], [key.lower(), 'arg1', 'arg2'])
        self.assertEqual(value.string, key.lower())

        value, args = matcher.match(
            [key], [key.upper(), 'arg1', 'arg2'])
        self.assertEqual(value.string, key.upper())

    def test_match_tries_all_options(self):
        options = ['foo', 'bar', 'glob']
        matcher = RegexMatch()
        for key in options:
            value, args = matcher.match(options, [key] + options)
            self.assertEqual(value.string, key)

    def test_match_strips_first_argument(self):
        matcher = RegexMatch()
        value, args = matcher.match(['test'], ['test', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_no_match_does_not_strip_first_argument(self):
        matcher = RegexMatch()
        value, args = matcher.match(['test'], ['arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])


class TestFolderMatch(TestCase):

    def test_entire_arg_is_folder_matches(self):
        testargs = ['[folder]', 'arg1', 'arg2']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_folder_name_strips_surrounding_whitespace(self):
        testargs = ['[ folder ]', 'arg1', 'arg2']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_folder_starts_mid_arg_matches(self):
        testargs = ['start [folder]', 'arg1', 'arg2']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['start', 'arg1', 'arg2'])

    def test_folder_ends_mid_arg_matches(self):
        testargs = ['start [folder] end', 'arg1', 'arg2']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['start end', 'arg1', 'arg2'])

    def test_folder_spans_multiple_args_matches(self):
        testargs = ['start [folder', 'name', 'is', 'test] end', 'arg1', 'arg2']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder name is test')
        self.assertEqual(args, ['start end', 'arg1', 'arg2'])

    def test_folder_spans_multiple_args_without_extra_args(self):
        testargs = ['[folder', 'name', 'is', 'test ]']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder name is test')
        self.assertEqual(args, [])

    def test_no_folder_close_bracket_does_not_match(self):
        testargs = ['[folder', 'name', 'is', 'test']
        matcher = FolderMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, None)
        self.assertEqual(args, testargs)


class TestEqualityMatch(TestCase):

    def test_equality_matches(self):
        options = ['foo']
        matcher = EqualityMatch()
        value, args = matcher.match(options, ['foo', 'bar'])
        self.assertEqual(value, options[0])

    def test_does_not_match_second_argument(self):
        options = ['bar']
        matcher = EqualityMatch()
        value, args = matcher.match(options, ['foo', 'bar'])
        self.assertEqual(value, None)

    def test_match_ignores_case(self):
        key = 'tESt'
        matcher = EqualityMatch()
        value, args = matcher.match(
            [key], [key.lower(), 'arg1', 'arg2'])
        self.assertEqual(value, key)

        value, args = matcher.match(
            [key], [key.upper(), 'arg1', 'arg2'])
        self.assertEqual(value, key)

    def test_match_tries_all_options(self):
        options = ['foo', 'bar', 'glob']
        matcher = EqualityMatch()
        for key in options:
            value, args = matcher.match(options, [key] + options)
            self.assertEqual(value, key)

    def test_match_strips_first_argument(self):
        matcher = EqualityMatch()
        value, args = matcher.match(['test'], ['test', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_no_match_does_not_strip_first_argument(self):
        matcher = EqualityMatch()
        value, args = matcher.match(['test'], ['arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])


class TestAlwaysMatch(TestCase):

    def test_matches_with_no_options(self):
        matcher = AlwaysMatch()
        value, args = matcher.match([], ['test', 'foo', 'bar'])
        self.assertEqual(value, 'test')

    def test_matches_returns_arg_found_exactly(self):
        matcher = AlwaysMatch()
        value, args = matcher.match(['option1'], ['tESt', 'foo', 'bar'])
        self.assertEqual(value, 'tESt')

    def test_strips_first_arg(self):
        matcher = AlwaysMatch()
        value, args = matcher.match(['option1'], ['tESt', 'foo', 'Bar'])
        self.assertEqual(args, ['foo', 'Bar'])


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


class TestPassthroughFormat(TestCase):
    def test_values_are_left_untouched(self):
        formatter = PassthroughFormat()
        value = ['a', 'b', 'C']
        output = formatter.format(value)
        self.assertEqual(value, output)

    def test_empty_list_returns_empty_list(self):
        formatter = PassthroughFormat()
        output = formatter.format([])
        self.assertEqual(output, [])


class TestApplyFunctionFormat(TestCase):
    def test_format_function_is_applied_to_value(self):
        class MockFormatFunction():
            def __init__(self):
                self.call_list = []

            def mock_format(self, value):
                self.call_list.append(value)
                return value
        mock_ff = MockFormatFunction()
        formatter = ApplyFunctionFormat(format_function=mock_ff.mock_format)
        value = ['arg1', 'arg2']
        formatter.format(value)
        self.assertEqual(mock_ff.call_list, [value, ])


class MockDateMatch():
    def __init__(self, offset=None, interval=None):
        self.offset = offset
        self.interval = interval

    def groups(self):
        if self.offset and self.interval:
            return (
                'due', '+',
                '{}'.format(self.offset),
                '{}'.format(self.interval)
            )
        else:
            return ('due', )

    def group(self, index):
        if index == 0:
            if self.offset and self.interval:
                return 'due+{}{}'.format(self.offset, self.interval)
            else:
                return 'due'
        if index == 1 or index == 'name':
            return 'due'
        if not (self.offset and self.interval):
            raise IndexError
        if index == 2 or index == 'sign':
            return '+'
        if index == 3 or index == 'offset':
            return '{}'.format(self.offset)
        if index == 4 or index == 'interval':
            return '{}'.format(self.interval)
        raise IndexError


class TestDateFormat(TestCase):

    def test_no_date_offset_returns_max_date(self):
        max_date = date(9999, 12, 31)
        formatter = DateFormat()
        match = MockDateMatch()
        output = formatter.format([match, ])
        self.assertEqual(output, max_date)

    def test_day_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(days=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'd')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_week_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(weeks=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'w')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_month_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(months=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'm')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)

    def test_year_offset_shifts_date_by_correct_amount(self):
        offset = date.today()
        offset += relativedelta(years=5)
        formatter = DateFormat()
        match = MockDateMatch(5, 'y')
        output = formatter.format([match, ])
        self.assertEqual(output, offset)
