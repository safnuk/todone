from unittest import TestCase

from todone.argparser import (
    AbstractMatch,
    AbstractTransform,
    AlwaysMatch,
    Argument,
    EqualityMatch,
    Nargs,
    RegexMatch,
    SubstringMatch,
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
            self.match_limit += 1
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
        argmatcher = Argument.create(name='name', options=[])
        self.assertTrue(issubclass(type(argmatcher), EqualityMatch))

    def test_created_argument_saves_name(self):
        argmatcher = Argument.create(name='test')
        self.assertTrue(argmatcher.name, 'test')

    def test_created_argument_saves_options(self):
        options = ['foo', 'bar']
        argmatcher = Argument.create(name='test', options=options)
        self.assertTrue(argmatcher.options, options)

    def test_create_used_passed_match_class(self):
        argmatcher = Argument.create(name='test', match=RegexMatch)
        self.assertTrue(issubclass(type(argmatcher), RegexMatch))


class TestArgument(TestCase):

    def test_default_values(self):
        parser = Argument(name='test')
        self.assertEqual(parser.name, 'test')
        self.assertEqual(parser.options, None)
        self.assertEqual(parser.positional, True)
        self.assertTrue(issubclass(type(parser.nargs), Nargs))
        self.assertTrue(parser.nargs.min == parser.nargs.max == 1)
        self.assertTrue(issubclass(type(parser), AbstractMatch))
        self.assertTrue(issubclass(type(parser), AbstractTransform))


class TestPositionalArgument(TestCase):

    def test_parse_arg_stops_on_first_nonmatch(self):
        parser = Argument.create(
            name='name', positional=True, nargs=3, match_limit=2,
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
        for n in range(1, 7):
            parser = Argument.create(
                name='name', positional=True,
                nargs=n,
                match=MockAlwaysMatch)
            args = ['foo', 'bar', 'buzz', 'baz']
            key, value, unmatched_args = parser.parse(args)
            calls = n if n < 5 else 4
            self.assertEqual(len(parser.call_list), calls)
            self.assertEqual(value, args[:n])
            self.assertEqual(unmatched_args, args[n:])

    def test_parse_arg_returns_null_key_when_no_match(self):
        parser = Argument.create(
            name='name', positional=True, match_limit=0,
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
            name='name', positional=False, nargs=3, match_limit=2,
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
            name='name', positional=False, nargs=3, match_limit=2,
            match=MockAlternatingMatch
        )
        args = ['foo', 'bar', 'buzz', 'baz']
        key, value, remaining_args = parser.parse(args)
        self.assertEqual(value, ['foo', 'buzz'])

    def test_parse_arg_returns_unmatched_args(self):
        parser = Argument.create(
            name='name', positional=False, nargs=3, match_limit=2,
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
            name='name', positional=False, match_limit=0,
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
