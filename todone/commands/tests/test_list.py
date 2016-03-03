from datetime import date
from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone.backends import folders
from todone.backends.db import Todo
from todone.commands.list import parse_args

in_memory_db = peewee.SqliteDatabase(':memory:')


class TestListWithDB(TestCase):

    def run(self, result=None):
        with test_database(in_memory_db, [Todo, ]):
            super().run(result)


class TestListArgParse(TestCase):

    def test_parse_args_parses_filename(self):
        args = parse_args(['.filename'])
        self.assertEqual(args['file'], 'filename')
        args = parse_args(['.filename', 'string1', '.string2'])
        self.assertEqual(args['file'], 'filename')
        args = parse_args(['string', 'filename'])
        self.assertEqual(args['file'], None)
        args = parse_args(['string1', 'string2', 'string.3'])
        self.assertEqual(args['file'], None)

    def test_parse_args_records_folder(self):
        args = parse_args(['today'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['.file', 'today'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['tod', 'done'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['.file', 'string', 'today'])
        self.assertFalse(args['folder'])
        args = parse_args(['string', 'today'])
        self.assertFalse(args['folder'])

    def test_parse_args_parses_due_keyword(self):
        max_date = date(9999, 12, 31)
        args = parse_args(['due'])
        self.assertEqual(args['due'], max_date)
        args = parse_args(['.file', 'Due'])
        self.assertEqual(args['due'], max_date)
        args = parse_args(['.file', 'done', 'D+0d'])
        self.assertEqual(args['due'], date.today())
        args = parse_args(['.file', 'inbox', '@Work', 'r+5m', 'D+0d'])
        self.assertEqual(args['due'], date.today())

    def test_parse_args_parses_remind_keyword(self):
        max_date = date(9999, 12, 31)
        args = parse_args(['remind'])
        self.assertEqual(args['remind'], max_date)
        args = parse_args(['.file', 'remind'])
        self.assertEqual(args['remind'], max_date)
        args = parse_args(['.file', 'done', 'R+0d'])
        self.assertEqual(args['remind'], date.today())
        args = parse_args(['.file', 'inbox', '@Work', 'd+5m', 'r+0d'])
        self.assertEqual(args['remind'], date.today())

    def test_parse_args_parses_search_keywords(self):
        keywords = ['search', 'test', 'words']
        args = parse_args(keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file'] + keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file', 'today'] + keywords)
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(['.file', 'today'] + keywords + ['due+3w'])
        self.assertEqual(args['keywords'], keywords)
        args = parse_args(keywords + ['due+3w'] + ['.file', 'today'])
        self.assertEqual(args['keywords'], keywords + ['.file', 'today'])
        self.assertFalse(args['file'])
        self.assertFalse(args['folder'])
