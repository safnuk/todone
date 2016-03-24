import datetime
import dateutil.relativedelta
import re


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


class FolderMatch(AbstractMatch):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        regex = r'(?P<start>[\S]+)/(?P<end>.*)'
        match = re.match(regex, args[0])
        if match:
            matches = []
            for keyword in targets:
                if keyword.lower().startswith(
                        match.group('start').lower()
                ):
                    matches.append((keyword, match.group('end').strip()))
            if len(matches) == 1:
                unmatched_args = (
                    [matches[0][1]] + args[1:] if matches[0][1]
                    else args[1:]
                )
                return matches[0][0], unmatched_args
            else:
                raise ArgumentError
        return None, args


class FlagKeywordMatch(SubstringMatch):

    def match(self, target, args):
        if args and (args[0] in ['-', '--']):
            return None, args
        value, args = super().match(target, args)
        if value:
            return args[0], args[1:]
        else:
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


class ProjectMatch(AbstractMatch):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def match(self, targets, args):
        regex = r'(?P<start>[^[]*)\[(?P<folder>[^\]]+)\](?P<end>.*)'
        regex_match = re.fullmatch(regex, args[0], re.IGNORECASE)
        if regex_match:
            arg_start = regex_match.group('start').strip()
            arg_end = regex_match.group('end').strip()
            # strip combined arg to leave empty string if both empty
            arg = (arg_start + ' ' + arg_end).strip()
            remaining_args = [arg] + args[1:] if arg else args[1:]
            return regex_match.group('folder').strip(), remaining_args
        regex_start = r'(?P<start>[^[]*)\[(?P<folder_start>[^\]]+)'
        regex_end = r'(?P<folder_end>[^\]]*)\](?P<end>.*)'
        regex_match_start = re.fullmatch(regex_start, args[0])
        if regex_match_start:
            folder = []
            arg_start = regex_match_start.group('start').strip()
            folder.append(regex_match_start.group('folder_start').strip())
            for n, arg in enumerate(args[1:]):
                regex_match_end = re.fullmatch(regex_end, arg)
                if regex_match_end:
                    folder.append(regex_match_end.group('folder_end').strip())
                    arg_end = regex_match_end.group('end').strip()
                    # strip combined arg to leave empty string if both empty
                    firstarg = (arg_start + ' ' + arg_end).strip()
                    remaining_args = (
                        [firstarg] + args[n+2:] if firstarg else args[n+2:]
                    )
                    return ' '.join(folder), remaining_args
                else:
                    folder.append(arg)
        return None, args


class AbstractFormat(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, value):
        raise NotImplementedError("Subclass must implement virtual method")


class ApplyFunctionFormat(AbstractFormat):
    def __init__(self, format_function=None, *args, **kwargs):
        self.format_function = format_function
        super().__init__(*args, **kwargs)

    def format(self, value):
        if self.format_function:
            return self.format_function(value)
        return value


class PassthroughFormat(ApplyFunctionFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class DateFormat(AbstractFormat):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def format(self, values):
        if not values:
            return None
        value = values[0]
        offset_date = datetime.date.today()
        if len(value.groups()) == 1:
            return datetime.date(9999, 12, 31)
        offset = int(value.group('offset'))
        interval = value.group('interval').lower()
        if 'days'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(days=offset)
        elif 'weeks'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(weeks=offset)
        elif 'months'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(months=offset)
        elif 'years'.startswith(interval):
            offset_date += dateutil.relativedelta.relativedelta(years=offset)
        return offset_date


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


class ArgumentError(Exception):
    pass
