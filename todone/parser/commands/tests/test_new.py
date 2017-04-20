from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase

from todone.parser.commands.new import parse_args


class TestNewArgParse(TestCase):

    def test_parse_args_folder_is_optional(self):
        args = parse_args(['New', 'todo'])
        self.assertFalse(args['folder'])
        args = parse_args(['New', 'today/', 'todo'])
        self.assertFalse(args['folder'])

    def test_parse_args_parses_folder(self):
        args = parse_args(['toDay/', 'New', 'todo'])
        self.assertEqual(args['folder'], 'today')
        args = parse_args(['iN/', 'today', 'todo'])
        self.assertEqual(args['folder'], 'in')
        args = parse_args(['iNbox/today', 'todo'])
        self.assertEqual(args['folder'], 'inbox')

    def test_parse_args_concats_todo_title(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['action'], 'New todo')

    def test_parse_args_parses_due_keyword(self):
        today = date.today()
        args = parse_args(['due+1m', 'Test todo'])
        self.assertEqual(args['due'], today + relativedelta(months=1))
