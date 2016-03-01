import re

from todone.commands import COMMAND_MAPPING


class AbstractMatch(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, target, args):
        raise NotImplementedError("Subclass must implement virtual method")


class AlwaysMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, target, args):
        return args[0], args[1:]


class EqualityMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        for keyword in targets:
            if keyword.lower() == args[0].lower():
                return keyword, args[1:]
        return None, args


class SubstringMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        matches = []
        for keyword in targets:
            if keyword.lower().startswith(args[0].lower()):
                matches.append(keyword)
        if len(matches) == 1:
            return matches[0], args[1:]
        return None, args


class RegexMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        for regex in targets:
            regex_match = re.fullmatch(regex, args[0], re.IGNORECASE)
            if regex_match:
                return regex_match, args[1:]
        return None, args


class AbstractTransform(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def transform(self, value):
        raise NotImplementedError("Subclass must implement virtual method")


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


class Argument(AbstractMatch, AbstractTransform):
    """
    Class which attempts to match a specified type of argument
    from a list of arguments. Use factory function create, with arguments:
        name:    Name assigned to the argument; used as dictionary key
                 for parsed arguments.
        options: List of keywords or expressions that will match
                 the argument.
        nargs:   Number of arguments to search for. Can be: any positive
                 integer; '*' (any number of arguments is acceptable);
                 '+' (at last one match required); '?' (either 0 or
                 1 match). Throws an InvalidArgument exception if
                 incorrect number of matches found.
        positional: If True, arg(s) must appear at the start of the list,
                    so the search for matches will stop at the first
                    non-match, or enough matches are found, whichever
                    comes first. If False, every arg is searched, until
                    enough matches are found (as specified by nargs).
        Match:      Class which provides match logic; must inherit from
                    AbstractMatch. Typical choices include
                    EqualityMatch, SubstringMatch, RegexMatch,
                    AlwaysMatch.
        Transform:  Class which transforms matched arguments; must
                    inherit from AbstractTransform. Typical choices are
                    PassthroughTransform, FunctionTransform.
    """

    def __init__(
        self, name, options=None, positional=True,
        nargs=1, *args, **kwargs
    ):
        self.name = name
        self.options = [x for x in options] if options else None
        self.positional = positional
        self.nargs = Nargs(nargs)
        super().__init__(*args, **kwargs)

    @staticmethod
    def create(
        name,
        match=EqualityMatch,
        transform=AbstractTransform,
        *args, **kwargs
    ):
        class CustomArgument(Argument, match, transform):
            pass

        return CustomArgument(name, *args, **kwargs)

    def parse(self, args):
        parsed = []
        unmatched_args = []
        while args and (len(parsed) < self.nargs.max):
            value, args = self.match(self.options, args)
            if value is not None:
                parsed.append(value)
            elif self.positional:
                break
            else:
                unmatched_args.append(args[0])
                args = args[1:]
        key = self.name if parsed else None
        unmatched_args += args
        return key, parsed, unmatched_args


class Nargs:
    MINS = {
        '?': 0,
        '+': 1,
        '*': 0,
    }
    MAXS = {
        '?': 1,
        '+': float('inf'),
        '*': float('inf'),
    }

    def __init__(self, nargs):
        try:
            self.min = int(nargs)
            self.max = int(nargs)
        except ValueError or TypeError:
            self.min = Nargs.MINS[nargs]
            self.max = Nargs.MAXS[nargs]


PARSE_INIT = [
    {'name': 'command', 'options': COMMAND_MAPPING},
    {
        'name': 'args', 'options': [r'.+', ],
        'nargs': '+',
        'positional': False,
    },
]
