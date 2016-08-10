from unittest import TestCase

from todone.parser.exceptions import ArgumentError
from todone.parser.match import (
    AlwaysMatch,
    EqualityMatch,
    FlagKeywordMatch,
    FolderMatch,
    ProjectMatch,
    RegexMatch,
    SubstringMatch,
)


class TestFolderMatch(TestCase):

    def test_match_all_substrings(self):
        key = 'test'
        matcher = FolderMatch()
        for n in range(1, len(key)):
            value, args = matcher.match([key], [key[:n] + '/', 'arg1', 'arg2'])
            self.assertEqual(value, key)

    def test_match_ignores_case(self):
        key = 'tESt'
        matcher = FolderMatch()
        for n in range(1, len(key)):
            value, args = matcher.match(
                [key], [key[:n].lower() + '/', 'arg1', 'arg2'])
            self.assertEqual(value, key)

            value, args = matcher.match(
                [key], [key[:n].upper() + '/', 'arg1', 'arg2'])
            self.assertEqual(value, key)

    def test_match_tries_all_options(self):
        options = ['foo', 'bar', 'glob']
        matcher = FolderMatch()
        for key in options:
            value, args = matcher.match(options, [key + '/'] + options)
            self.assertEqual(value, key)

    def test_raises_ArgumentError_on_ambiguous_substrings(self):
        options = ['foo', 'foa', 'fat']
        matcher = FolderMatch()
        with self.assertRaises(ArgumentError):
            value, args = matcher.match(options, ['f/'])
        with self.assertRaises(ArgumentError):
            value, args = matcher.match(options, ['fo/'])

    def test_match_only_unambiguous_substrings(self):
        options = ['foo', 'foa', 'fat']
        matcher = FolderMatch()
        value, args = matcher.match(options, ['foo/'])
        self.assertEqual(value, 'foo')
        value, args = matcher.match(options, ['foa/'])
        self.assertEqual(value, 'foa')
        value, args = matcher.match(options, ['fa/'])
        self.assertEqual(value, 'fat')

    def test_match_strips_first_argument(self):
        matcher = FolderMatch()
        value, args = matcher.match(['test'], ['test/', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_no_match_does_not_strip_first_argument(self):
        matcher = FolderMatch()
        value, args = matcher.match(['test'], ['arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_partial_match_returns_remainder_of_first_argument(self):
        matcher = FolderMatch()
        value, args = matcher.match(['test'], ['test/me', 'arg1', 'arg2'])
        self.assertEqual(args, ['me', 'arg1', 'arg2'])
        self.assertEqual(value, 'test')

    def test_partial_match_strips_leading_whitespace_of_args(self):
        matcher = FolderMatch()
        value, args = matcher.match(['test'], ['test/ me out', 'arg1', 'arg2'])
        self.assertEqual(args, ['me out', 'arg1', 'arg2'])
        self.assertEqual(value, 'test')

    def test_partial_match_ignores_leading_whitespace_for_returned_args(self):
        matcher = FolderMatch()
        value, args = matcher.match(['test'], ['test/ ', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg1', 'arg2'])
        self.assertEqual(value, 'test')


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


class TestFlagKeywordMatch(TestCase):

    def test_on_flag_match_returns_next_arg(self):
        matcher = FlagKeywordMatch()
        value, args = matcher.match(['-c'], ['-c', 'config.ini'])
        self.assertEqual(value, 'config.ini')

    def test_does_not_match_single_minus(self):
        matcher = FlagKeywordMatch()
        value, args = matcher.match(['-c', '--config'], ['-', 'config.ini'])
        self.assertEqual(value, None)
        value, args = matcher.match(['-c'], ['-', 'config.ini'])
        self.assertEqual(value, None)

    def test_does_not_match_double_minus(self):
        matcher = FlagKeywordMatch()
        value, args = matcher.match(['-c', '--config'], ['--', 'config.ini'])
        self.assertEqual(value, None)

    def test_no_match_does_not_strip_first_argument(self):
        matcher = FlagKeywordMatch()
        value, args = matcher.match(['--test'], ['--arg1', 'arg2'])
        self.assertEqual(args, ['--arg1', 'arg2'])

    def test_match_strips_first_two_arguments(self):
        matcher = FlagKeywordMatch()
        value, args = matcher.match(['--test'], ['--test', 'arg1', 'arg2'])
        self.assertEqual(args, ['arg2'])


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


class TestProjectMatch(TestCase):

    def test_entire_arg_is_folder_matches(self):
        testargs = ['[folder]', 'arg1', 'arg2']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_folder_name_strips_surrounding_whitespace(self):
        testargs = ['[ folder ]', 'arg1', 'arg2']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['arg1', 'arg2'])

    def test_folder_starts_mid_arg_matches(self):
        testargs = ['start [folder]', 'arg1', 'arg2']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['start', 'arg1', 'arg2'])

    def test_folder_ends_mid_arg_matches(self):
        testargs = ['start [folder] end', 'arg1', 'arg2']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder')
        self.assertEqual(args, ['start end', 'arg1', 'arg2'])

    def test_folder_spans_multiple_args_matches(self):
        testargs = ['start [folder', 'name', 'is', 'test] end', 'arg1', 'arg2']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder name is test')
        self.assertEqual(args, ['start end', 'arg1', 'arg2'])

    def test_folder_spans_multiple_args_without_extra_args(self):
        testargs = ['[folder', 'name', 'is', 'test ]']
        matcher = ProjectMatch()
        value, args = matcher.match(None, testargs)
        self.assertEqual(value, 'folder name is test')
        self.assertEqual(args, [])

    def test_no_folder_close_bracket_does_not_match(self):
        testargs = ['[folder', 'name', 'is', 'test']
        matcher = ProjectMatch()
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
