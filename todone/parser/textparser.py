from todone.parser import exceptions as pe
from todone.parser import format as pf
from todone.parser import match


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
            raise pe.ArgumentError()


class Argument(match.AbstractMatch, pf.AbstractFormat):
    """
    Class which attempts to match a specified type of argument
    from a list of arguments. Use factory function :func:`create`
    to creat an argument.

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
        match=match.EqualityMatch,
        format=pf.PassthroughFormat,
        *args, **kwargs
    ):
        """Factory function to create an :class:`Argument` instance.

        :param name: name assigned to the argument;
            use as a dictionary key for the parsed arguments.
        :param options: list of keywords or expressions that will
            match the argument.
        :param nargs: number of arguments to search for; can be:
                * any positive integer
                * '*' (any number of arguments is acceptable)
                * '+' (at last one match required)
                * '?' (either 0 or 1 match).

            Raises an :class:`InvalidArgument` exception if incorrect number
            of matches found
        :param positional: if :data:`True`, arg(s) must appear at the
            start of the list, so the search for matches will stop at the first
            non-match, or enough matches are found, whichever
            comes first. If False, every arg is searched, until
            enough matches are found (as specified by nargs)
        :param Match: class which provides match logic;
            must inherit from :class:`AbstractMatch`.
            Typical choices include :class:`EqualityMatch`,
            :class:`SubstringMatch`, :class:`RegexMatch`,
            :class:`AlwaysMatch`
        :param Transform: class which transforms matched arguments;
            must inherit from :class:`AbstractTransform`;
            typical choices are :class:`PassthroughTransform`,
            :class:`FunctionTransform`
        """
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
            raise pe.ArgumentError()
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
