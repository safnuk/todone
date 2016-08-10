import enum

from todone.parser.format import (
    ApplyFunctionFormat,
)
from todone.parser.match import (
    AlwaysMatch,
)
from todone.parser.textparser import TextParser


class PresetArgument(enum.Enum):
    all_remaining = 1
    required_switch = 2
    optional_switch = 3
    index = 4
    folder = 5
    folder_with_default = 6
    unique_project = 7
    all_matching_projects = 8
    due_date = 9
    remind_date = 10
    file = 11


PRESET_ARGUMENTS = {
    PresetArgument.all_remaining: {
        'match': AlwaysMatch,
        'nargs': '*',
        'format': ApplyFunctionFormat,
        'format_function': ' '.join
    }
}


class ParserFactory():
    @classmethod
    def from_arg_list(cls, args=[]):
        parser = TextParser()
        for (arg, keywords) in args:
            parser.add_argument(**dict(PRESET_ARGUMENTS[arg], **keywords))
        return parser
