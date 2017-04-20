from contextlib import redirect_stdout
import io
import textwrap
from unittest import TestCase

import todone.backend.dispatch as dispatch
import todone.backend.commands as cmd


class TestHelpText(TestCase):

    def test_no_args_prints_default_help(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Help.run({})
        s = f.getvalue()
        self.assertIn(textwrap.dedent(cmd.Help.long_help), s)

    def test_help_arg_prints_default_help(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Help.run({'subcommand': 'help'})
        s = f.getvalue()
        self.assertIn(textwrap.dedent(cmd.Help.run.__doc__), s)

    def test_list_arg_prints_list_docstring(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Help.run({'subcommand': 'list'})
        s = f.getvalue()
        self.assertIn(textwrap.dedent(cmd.List.run.__doc__), s)

    def test_short_flag_prints_short_help_string(self):
        f = io.StringIO()
        with redirect_stdout(f):
            cmd.Help.run({'short': '--short', 'subcommand': 'help'})
        s = f.getvalue()
        self.assertIn(cmd.Help.run.short_help, s)

    def test_all_commands_define_short_help_strings(self):
        for command in dispatch.COMMAND_MAPPING:
            # does not raise exception
            cmd.Help.run({'short': '--short', 'subcommand': command})
