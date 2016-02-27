from unittest import TestCase

from todone.argparser import Argument, ArgParser, PARSE_INIT
from todone.commands import COMMAND_MAPPING


class TestArgParser(TestCase):
    # def setUp(self):
    #     self.parser = ArgParser()
    #     self.parser.add_argument('command', options=COMMAND_MAPPING)

    def test_add_argument_with_command_list(self):
        parser = ArgParser()
        parser.add_argument(name='command', options=COMMAND_MAPPING)
        self.assertEqual(len(parser.arguments), 1)
        arg = parser.arguments[0]
        self.assertEqual(arg.options, [x for x in COMMAND_MAPPING])
        self.assertEqual(arg.name, 'command')

    def test_init_with_arg_list(self):
        arglist = [{'name': 'test'}, {'name': 'foo'}]
        parser = ArgParser(arglist)
        self.assertEqual(len(parser.arguments), 2)
        self.assertEqual(parser.arguments[0].name, 'test')
        self.assertEqual(parser.arguments[1].name, 'foo')

    def test_command_is_parsed(self):
        parser = ArgParser(PARSE_INIT)
        for command in COMMAND_MAPPING:
            for n in range(1, len(command)):
                args = parser.parse_args([command[:n], 'Test', 'todo'])
                self.assertEqual(args['command'], command)
                self.assertEqual(args['args'], ['Test', 'todo'])

                args = parser.parse_args([command[:n].lower(), 'Test', 'todo'])
                self.assertEqual(args['command'], command)
                self.assertEqual(args['args'], ['Test', 'todo'])


class TestArgument(TestCase):

    @staticmethod
    def mock_always_match(parser, args):
        return args[0], args[1:]

    def test_default_values(self):
        parser = Argument(name='test')
        self.assertEqual(parser.name, 'test')
        self.assertEqual(parser.options, None)
        self.assertEqual(parser.positional, True)
        self.assertEqual(parser.nargs, 1)
        self.assertEqual(parser.matcher, Argument.match_start)
        self.assertEqual(parser.transformer, Argument.passthrough)

    def test_parse_arg_calls_matcher_once_when_nargs_1(self):
        parser = Argument(name='name', options=['test', 'WORD'],
                          matcher=self.mock_always_match)
        args = ['arg1', 'arg2']
        parsed = parser.parse_arg(args)
        self.assertEqual(parsed, ('name', 'arg1', ['arg2', ]))

    def test_parse_arg_calls_matcher_on_each_arg_when_nargs_multiple(self):
        parser = Argument(name='name', options=['test', 'WORD'],
                          nargs='+', matcher=self.mock_always_match)
        args = ['arg1', 'arg2', 'arg3']
        key, value, remaining_args = parser.parse_arg(args)
        self.assertEqual(key, 'name')
        self.assertEqual(value, args)
        self.assertEqual(remaining_args, [])

    def test_match_start(self):
        parser = Argument(name='name', options=['test', 'WORD'])
        key1 = 'test'
        key2 = 'word'
        for n in range(1, 4):
            value, args = parser.match_start([key1[:n], 'arg1', 'arg2'])
            self.assertEqual(value, 'test')
            self.assertEqual(args, ['arg1', 'arg2'])
            value, args = parser.match_start(
                [key1.upper()[:n], 'arg1', 'arg2'])
            self.assertEqual(value, 'test')
            self.assertEqual(args, ['arg1', 'arg2'])
            value, args = parser.match_start([key2[:n], 'arg1', 'arg2'])
            self.assertEqual(value, 'WORD')
            self.assertEqual(args, ['arg1', 'arg2'])
            value, args = parser.match_start(
                [key2.upper()[:n], 'arg1', 'arg2'])
            self.assertEqual(value, 'WORD')
            self.assertEqual(args, ['arg1', 'arg2'])

    def test_match_regex(self):
        parser = Argument(
            name='name',
            options=[
                r'(due|du|d)\+(\d+)(d|w|m|y)',
                r'(due|du|d)',
            ],
            matcher=Argument.match_regex,
        )
        testargs = [
            ['due', 'test'],
            ['DU', 'test'],
            ['Due+5w'],
        ]
        for testarg in testargs:
            value, args = parser.match_regex(testarg)
            self.assertEqual(value, testarg[0])
            self.assertEqual(args, testarg[1:])
