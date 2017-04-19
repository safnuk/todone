from contextlib import redirect_stdout
import io
import textwrap
from unittest import TestCase

import todone.commands.dispatch
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

    def test_short_flag_prints_short_help_string(self):
        f = io.StringIO()
        with redirect_stdout(f):
            help_text(['--short', 'help'])
        s = f.getvalue()
        self.assertIn(help_text.short_help, s)

    def test_all_commands_define_short_help_strings(self):
        for command in todone.commands.dispatch.COMMAND_MAPPING:
            # does not raise exception
            help_text(['--short', command])
