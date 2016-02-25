from datetime import date
from dateutil.relativedelta import relativedelta
from unittest import TestCase

from todone.backends import folders
from todone.commands.new import parse_args, parse_folder


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
        self.assertEqual(args['todo'], 'New todo')

    def test_parse_folder(self):
        self.assertEqual(parse_folder(''), None)
        allowed = [
            folders.INBOX, folders.TODAY, folders.NEXT,
            folders.SOMEDAY, folders.CAL
        ]
        for folder in allowed:
            for n in range(1, len(folder)):
                response = parse_folder(folder[:n])
                self.assertEqual(response, folder)
                response = parse_folder(folder[:n].lower())
                self.assertEqual(response, folder)
                if len(folder[n:]) > 1:
                    response = parse_folder(folder[n:])
                    self.assertEqual(response, None)
        for folder in [x for x in folders.FOLDERS if x not in allowed]:
            response = parse_folder(folder)
            self.assertEqual(response, None)
            response = parse_folder(folder.lower())
            self.assertEqual(response, None)

    def test_parse_args_parses_due_keyword(self):
        today = date.today()
        args = parse_args(['due+1m', 'Test todo'])
        self.assertEqual(args['due'], today + relativedelta(months=1))
