import textwrap
from unittest import TestCase

import todone.backend.commands as cmd


class TestHelpText(TestCase):

    def test_no_args_should_output_default_help(self):
        s, r = cmd.Help.run({})
        self.assertEqual(s, 'success')
        self.assertIn(textwrap.dedent(cmd.Help.long_help), r)

    def test_help_arg_should_output_default_help(self):
        s, r = cmd.Help.run({'subcommand': 'help'})
        self.assertEqual(s, 'success')
        self.assertIn(textwrap.dedent(cmd.Help.long_help), r)

    def test_list_arg_prints_list_docstring(self):
        s, r = cmd.Help.run({'subcommand': 'list'})
        self.assertEqual(s, 'success')
        self.assertIn(textwrap.dedent(cmd.List.long_help), r)

    def test_short_flag_prints_short_help_string(self):
        s, r = cmd.Help.run({'short': '--short', 'subcommand': 'help'})
        self.assertEqual(s, 'success')
        self.assertIn(textwrap.dedent(cmd.Help.short_help), r)

    def test_all_commands_define_short_help_strings(self):
        for command in cmd.COMMAND_MAPPING:
            # does not raise exception
            cmd.Help.run({'short': '--short', 'subcommand': command})
