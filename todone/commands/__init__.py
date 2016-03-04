from todone.commands.help import help_text
from todone.commands.list import list_items
from todone.commands.new import new_todo
from todone.commands.setup import setup_db, version


def dispatch(action, args):
    COMMAND_MAPPING[action](args)

COMMAND_MAPPING = {
    '-h': help_text,
    '--h': help_text,
    '-v': version,
    '--v': version,
    'help': help_text,
    'list': list_items,
    'new': new_todo,
    'setup': setup_db,
}
