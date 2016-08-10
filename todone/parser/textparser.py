from todone.parser.exceptions import ArgumentError
from todone.parser.format import (
    AbstractFormat,
    PassthroughFormat
)
from todone.parser.match import (
    AbstractMatch,
    EqualityMatch,
)


class TextParser:
    def __init__(self):
        self.arguments = []
        self.parsed_data = {}

    def add_argument(self, *args, **kwargs):
        self.arguments.append(Argument.create(*args, **kwargs))

    def parse(self, args):
        for arg in self.arguments:
            key, value, args = arg.parse(args)
            self.parsed_data[key] = value
        if args:
            raise ArgumentError()


class Argument(AbstractMatch, AbstractFormat):
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
        nargs=1, default=[], *args, **kwargs
    ):
        self.name = name
        self.options = [x for x in options] if options else None
        self.positional = positional
        self.nargs = Nargs(nargs)
        self.default = default
        super().__init__(*args, **kwargs)

    @staticmethod
    def create(
        name,
        match=EqualityMatch,
        format=PassthroughFormat,
        *args, **kwargs
    ):
        class CustomArgument(Argument, match, format):
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
        unmatched_args += args
        if len(parsed) < self.nargs.min:
            raise ArgumentError()
        if self.default:
            parsed = parsed if parsed else self.default
        return self.name, self.format(parsed), unmatched_args


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
        except (ValueError, TypeError):
            self.min = Nargs.MINS[nargs]
            self.max = Nargs.MAXS[nargs]
