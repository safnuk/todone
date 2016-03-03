from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase

from todone.backends import folders
from todone.commands.new import parse_args


class TestNewArgParse(TestCase):

    def test_parse_args_defaults_to_inbox_folder(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)
        args = parse_args(['New', 'today', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_parses_valid_folder(self):
        args = parse_args(['toDay', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.TODAY)
        args = parse_args(['iN', 'today', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_does_not_parse_invalid_folder(self):
        args = parse_args(['done', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

        args = parse_args(['cancel', 'New', 'todo'])
        self.assertEqual(args['folder'], folders.INBOX)

    def test_parse_args_parsed_todo_title(self):
        args = parse_args(['New', 'todo'])
        self.assertEqual(args['action'], 'New todo')

    def test_parse_args_parses_due_keyword(self):
        today = date.today()
        args = parse_args(['due+1m', 'Test todo'])
        self.assertEqual(args['due'], today + relativedelta(months=1))
