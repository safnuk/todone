"""Generate a :class:`TextParser` class. Includes the following classes:

    - :class:`ParserFactory`
    - :class:`PresetArgument`
"""
import enum

from todone.parser import format as pf
from todone.parser import match
from todone.parser import textparser


DATE_REGEX = [
    r'({})',
    r'({})(?P<sign>[+-])(?P<offset>\d+)(?P<interval>[d|w|m|y])'
]
DUE_REGEX = [x.format('due|du|d') for x in DATE_REGEX]
FILE_REGEX = [r'\.(?P<file>.+)', ]
INDEX_REGEX = [r'(?P<index>\d+)', ]
REMIND_REGEX = [x.format('remind|remin|remi|rem|re|r') for x in DATE_REGEX]


class PresetArgument(enum.Enum):
    """:class:`Enum` of preconfigured argument parsers commonly used by
    many of todone's commands.
    """
    all_remaining = 1
    required_switch = 2
    optional_switch = 3
    index = 4
    folder = 5
    parent = 6
    due_date = 7
    remind_date = 8
    file = 9
    config = 10
    all_remaining_passthrough = 11

    @staticmethod
    def get_index(arg):
        if arg:
            return int(arg[0].group('index'))
        return None

    @staticmethod
    def get_file_name(x):
        if x:
            return x[0].group('file')
        return None


_PRESET_ARGUMENTS = {
    PresetArgument.all_remaining_passthrough: {
        'match': match.AlwaysMatch,
        'nargs': '*',
    },
    PresetArgument.all_remaining: {
        'match': match.AlwaysMatch,
        'nargs': '*',
        'format': pf.ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.required_switch: {
        'nargs': 1,
        'match': match.SubstringMatch,
        'format': pf.ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.optional_switch: {
        'nargs': '?',
        'format': pf.ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.index: {
        'options': INDEX_REGEX,
        'match': match.RegexMatch,
        'nargs': 1,
        'format': pf.ApplyFunctionFormat,
        'format_function': PresetArgument.get_index,
    },
    PresetArgument.folder: {
        'match': match.FolderMatch,
        'nargs': '?',
        'format': pf.ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.parent: {
        'match': match.ParentMatch,
        'nargs': '?',
        'format': pf.ApplyFunctionFormat,
        'format_function': lambda match: ({
            'folder': match[0], 'action': match[1]})
    },
    PresetArgument.due_date: {
        'options': DUE_REGEX,
        'match': match.RegexMatch,
        'nargs': '?',
        'format': pf.DateFormat,
        'positional': False,
    },
    PresetArgument.remind_date: {
        'options': REMIND_REGEX,
        'match': match.RegexMatch,
        'nargs': '?',
        'format': pf.DateFormat,
        'positional': False,
    },
    PresetArgument.file: {
        'match': match.RegexMatch,
        'options': FILE_REGEX,
        'nargs': '?',
        'format': pf.ApplyFunctionFormat,
        'format_function': PresetArgument.get_file_name,
    },
    PresetArgument.config: {
        'match': match.FlagKeywordMatch,
        'options': ['-c', '--config'],
        'nargs': '?',
        'format': pf.ApplyFunctionFormat,
        'format_function': ' '.join,
    }
}


class ParserFactory():
    """Factory class for generating a :class:`TextParser`."""
    @classmethod
    def from_arg_list(cls, args=[]):
        """Return a :class:`TextParser` constructed by passing a list of
        argument parsers

        :param args: List of dictionaries, each containing configuration
            options for an argument parser.

        """
        parser = textparser.TextParser()
        for (arg, keywords) in args:
            parser.add_argument(**dict(_PRESET_ARGUMENTS[arg], **keywords))
        return parser
