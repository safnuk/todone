import re

from todone.commands import COMMAND_MAPPING


class ArgParser:
    def __init__(self, arg_types=[]):
        self.arguments = []
        for arg in arg_types:
            self.arguments.append(Argument(**arg))

    def add_argument(self, name, options=None):
        self.arguments.append(Argument(name, options))

    def parse_args(self, args):
        parsed = {}
        for arg in self.arguments:
            key, value, args = arg.parse_arg(args)
            if key:
                parsed[key] = value
        return parsed


class Argument:
    """
    Class which attempts to match a specified type of argument
    from a list of arguments. Initialized with:
        name:    name assigned to the argument; used as dictionary key
                 for parsed arguments
        options: list of keywords or expressions that will match
                 the argument
        nargs:   number of arguments to search for; can be any positive
                 integer (search until exactly specified number found,
                 throw exceptions if search does not produce
                 enough results); '*' (search every argument for a match);
                 '+' (search every argument for a match, if at least
                 one not found, throw an exception); '?' (stop when one
                 match found, 0 matches is acceptable)
        positional: if true, arg(s) must appear at the start of the list
        matcher: function which checks for matches; must take
                 arguments of the instantiated Argument class and the
                 arg list being parsed; returns a triple
                    key, value, arglist
                 where key is the name of the argument, value is the
                 matched string from the arg list, and arglist is the
                 list of remaining arguments (with the matched one removed)
        transformer: function which transforms the matched argument;
                     default is to pass the raw string as input
    """

    def __init__(
        self, name, options=None, positional=True,
        nargs=1, matcher=None, transformer=None
    ):
        self.name = name
        self.options = [x for x in options] if options else None
        self.positional = positional
        self.nargs = nargs
        self.matcher = matcher if matcher else Argument.match_start
        self.transformer = (
            transformer if transformer else Argument.passthrough
        )

    def parse_arg(self, args):
        if self.nargs == 1:
            return self.matcher(self, args)
        parsed = []
        index = 0
        something_parsed = False
        while args[index:]:
            key, value, new_args = self.matcher(self, args[index:])
            if value:
                parsed.append(value)
            if key:
                something_parsed = True
            if args[index:] == new_args:
                index += 1
            else:
                args = args[:index] + new_args
        key = self.name if something_parsed else None
        return key, parsed, args

    def match_start(self, args):
        for match in self.options:
            if match.lower().startswith(args[0].lower()):
                return self.name, match, args[1:]
        return None, None, args

    def match_regex(self, args):
        for regex in self.options:
            if re.fullmatch(regex, args[0], re.IGNORECASE):
                return self.name, args[0], args[1:]
        return None, None, args

    def passthrough(self, arg):
        return arg


PARSE_INIT = [
    {'name': 'command', 'options': COMMAND_MAPPING},
    {
        'name': 'args', 'options': [r'.+', ],
        'matcher': Argument.match_regex,
        'nargs': '+',
        'positional': False,
    },
]
