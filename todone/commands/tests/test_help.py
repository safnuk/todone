from contextlib import redirect_stdout
import io
import textwrap
from unittest import TestCase

from todone.commands.help import help_text
from todone.commands.list import list_items

class TestHelpText(TestCase):

    def test_no_args_prints_default_help(self):
        f = io.StringIO()
        with redirect_stdout(f):
            help_text([])
        s = f.getvalue()
        self.assertIn(textwrap.dedent(help_text.__doc__), s)

    def test_help_arg_prints_default_help(self):
        f = io.StringIO()
        with redirect_stdout(f):
            help_text(['help'])
        s = f.getvalue()
        self.assertIn(textwrap.dedent(help_text.__doc__), s)

    def test_list_arg_prints_list_docstring(self):
        f = io.StringIO()
        with redirect_stdout(f):
            help_text(['list'])
        s = f.getvalue()
        self.assertIn(textwrap.dedent(list_items.__doc__), s)