from todone.commands.help import help_text
from todone.commands.list import list_items
from todone.commands.move import move_todo
from todone.commands.new import new_todo
from todone.commands.setup import setup_db, version
from todone.textparser import ArgumentError


def dispatch_command(action, args):
    try:
        COMMAND_MAPPING[action](args)
    except ArgumentError as e:
        print("Invalid argument(s) for {} command. {}".format(
            action, e))
        COMMAND_MAPPING['help'](['--short', action])

COMMAND_MAPPING = {
    '-h': help_text,
    '--help': help_text,
    'help': help_text,
    '-v': version,
    '--version': version,
    'version': version,
    'list': list_items,
    'move': move_todo,
    'new': new_todo,
    'setup': setup_db,
}
