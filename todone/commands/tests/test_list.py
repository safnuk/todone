from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase

import peewee
from playhouse.test_utils import test_database

from todone.backends import folders
from todone.backends.db import Todo
from todone.commands.list import parse_args, parse_folder, parse_keyword

in_memory_db = peewee.SqliteDatabase(':memory:')

class TestListWithDB(TestCase):
    
    def run(self, result=None):
        with test_database(in_memory_db, [Todo,]):
            super().run(result)

        
class TestListArgParse(TestCase):

    def test_parse_args_parses_filename(self):
        args = parse_args(['.filename'])
        self.assertEqual(args['file'], '.filename')
        args = parse_args(['.filename', 'string1', '.string2'])
        self.assertEqual(args['file'], '.filename')
        args = parse_args(['string', '.filename'])
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
        self.assertEqual(args['folder'], None)
        args = parse_args(['string', 'today'])
        self.assertEqual(args['folder'], None)

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
        self.assertEqual(args['file'], None)
        self.assertEqual(args['folder'], None)

    def test_parse_keywords_with_due(self):
        today = date.today()
        max_date = date(9999, 12, 31)

        key, response = parse_keyword('Due')
        self.assertEqual(key, 'due')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('D')
        self.assertEqual(key, 'due')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('dU')
        self.assertEqual(key, 'due')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('dues')
        self.assertEqual(key, None)
        self.assertEqual(response, None)

        key, response = parse_keyword('d+8d')
        self.assertEqual(key, 'due')
        self.assertEqual(response, today + relativedelta(days=8))

        key, response = parse_keyword('due+8w')
        self.assertEqual(key, 'due')
        self.assertEqual(response, today+relativedelta(weeks=8))
        
        key, response = parse_keyword('d+3m')
        self.assertEqual(key, 'due')
        self.assertEqual(response, today+relativedelta(months=3))

        key, response = parse_keyword('d+3y')
        self.assertEqual(key, 'due')
        self.assertEqual(response, today+relativedelta(years=3))

    def test_parse_keywords_with_remind(self):
        today = date.today()
        max_date = date(9999, 12, 31)

        key, response = parse_keyword('Remind')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('R')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('rE')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, max_date)

        key, response = parse_keyword('reminds')
        self.assertEqual(key, None)
        self.assertEqual(response, None)

        key, response = parse_keyword('r+8d')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, today + relativedelta(days=8))

        key, response = parse_keyword('rem+8w')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, today+relativedelta(weeks=8))
        
        key, response = parse_keyword('remI+3m')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, today+relativedelta(months=3))

        key, response = parse_keyword('reMin+3y')
        self.assertEqual(key, 'remind')
        self.assertEqual(response, today+relativedelta(years=3))


    def test_parse_folder(self):
        self.assertEqual(parse_folder(''), None)
        for folder in [x for x in folders.FOLDERS if x is not folders.DONE]:
            for n in range(1, len(folder)):
                response = parse_folder(folder[:n])
                self.assertEqual(response, folder)
                response = parse_folder(folder[:n].lower())
                self.assertEqual(response, folder)
                if len(folder[n:]) > 1:
                    response = parse_folder(folder[n:])
                    self.assertEqual(response, None)
        folder = folders.DONE
        self.assertEqual(parse_folder('d'), None)
        self.assertEqual(parse_folder('D'), None)
        self.assertEqual(parse_folder('ONE'), None)
        for n in range(2, len(folder)):
            response = parse_folder(folder[:n])
            self.assertEqual(response, folder)
            response = parse_folder(folder[:n].lower())
            self.assertEqual(response, folder)
