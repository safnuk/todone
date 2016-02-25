from todone.commands.help import help_text
from todone.commands.list import list_items
from todone.commands.new import new_todo

def dispatch(action, args):
    COMMAND_MAPPING[action](args)

COMMAND_MAPPING = {
    'help': help_text,
    'list': list_items,
    'new': new_todo,
}
