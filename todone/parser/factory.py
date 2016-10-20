import enum

from todone.backends.db import Todo
from todone.parser.format import (
    ApplyFunctionFormat,
    DateFormat,
)
from todone.parser.match import (
    AlwaysMatch,
    FolderMatch,
    ProjectMatch,
    RegexMatch,
    SubstringMatch,
)
from todone.parser.textparser import TextParser


DATE_REGEX = [
    r'({})',
    r'({})(?P<sign>[+-])(?P<offset>\d+)(?P<interval>[d|w|m|y])'
]
DUE_REGEX = [x.format('due|du|d') for x in DATE_REGEX]
FILE_REGEX = [r'\.(?P<file>.+)', ]
INDEX_REGEX = [r'(?P<index>\d+)', ]
REMIND_REGEX = [x.format('remind|remin|remi|rem|re|r') for x in DATE_REGEX]


class PresetArgument(enum.Enum):
    all_remaining = 1
    required_switch = 2
    optional_switch = 3
    index = 4
    folder = 5
    unique_project = 6
    all_matching_projects = 7
    due_date = 8
    remind_date = 9
    file = 10

    @staticmethod
    def get_index(arg):
        if arg:
            return int(arg[0].group('index'))
        return None

    @staticmethod
    def get_project_todo(x):
        if x:
            return Todo.get_projects(x[0])[0]
        return None

    @staticmethod
    def get_projects(x):
        if x:
            return Todo.get_projects(x[0])
        return None

    @staticmethod
    def get_file_name(x):
        if x:
            return x[0].group('file')
        return None


PRESET_ARGUMENTS = {
    PresetArgument.all_remaining: {
        'match': AlwaysMatch,
        'nargs': '*',
        'format': ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.required_switch: {
        'nargs': 1,
        'match': SubstringMatch,
        'format': ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.optional_switch: {
        'nargs': '?',
        'format': ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.index: {
        'options': INDEX_REGEX,
        'match': RegexMatch,
        'nargs': 1,
        'format': ApplyFunctionFormat,
        'format_function': PresetArgument.get_index,
    },
    PresetArgument.folder: {
        # TODO: Find a way to avoid calling Folder.select() when module loaded
        # 'options': list(Folder.select()),
        'match': FolderMatch,
        'nargs': '?',
        'format': ApplyFunctionFormat,
        'format_function': ' '.join,
    },
    PresetArgument.unique_project: {
        'match': ProjectMatch,
        'nargs': '?',
        'format': ApplyFunctionFormat,
        'format_function': PresetArgument.get_project_todo,
    },
    PresetArgument.all_matching_projects: {
        'match': ProjectMatch,
        'nargs': '?',
        'format': ApplyFunctionFormat,
        'format_function': PresetArgument.get_projects,
    },
    PresetArgument.due_date: {
        'options': DUE_REGEX,
        'match': RegexMatch,
        'nargs': '?',
        'format': DateFormat,
        'positional': False,
    },
    PresetArgument.remind_date: {
        'options': REMIND_REGEX,
        'match': RegexMatch,
        'nargs': '?',
        'format': DateFormat,
        'positional': False,
    },
    PresetArgument.file: {
        'match': RegexMatch,
        'options': FILE_REGEX,
        'nargs': '?',
        'format': ApplyFunctionFormat,
        'format_function': PresetArgument.get_file_name,
    },
}


class ParserFactory():
    @classmethod
    def from_arg_list(cls, args=[]):
        parser = TextParser()
        for (arg, keywords) in args:
            parser.add_argument(**dict(PRESET_ARGUMENTS[arg], **keywords))
        return parser
