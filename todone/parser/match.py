import re

from todone.parser.exceptions import ArgumentError


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
            elif len(matches) == 0:
                raise ArgumentError('No match found for folder {}/'.format(
                    match.group('start')
                ))
            else:
                raise ArgumentError(
                    'Multiple matches found for folder {}/'.format(
                        match.group('start')
                    ))
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
