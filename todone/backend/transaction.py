import datetime

from todone.backend import db


class Transaction:
    def __init__(self, command, args={}, timestamp=None):
        self.command = command
        self.args = args
        self.timestamp = timestamp if timestamp else datetime.datetime.now()

    def inverse(self):
        if self.command == 'new':
            todo = db.Todo.get(db.Todo.id == self.args['todo'])
            args = {
                'todo': todo.id,
                'old_folder': todo.folder.name,
                'new_folder': 'garbage'}
            return Transaction('move', args)
        elif self.command == 'move' and 'old_folder' in self.args:
            args = {
                'todo': self.args['todo'],
                'old_folder': self.args['new_folder'],
                'new_folder': self.args['old_folder']
            }
            return Transaction('move', args)
        elif self.command == 'move' and 'old_parent' in self.args:
            args = {
                'todo': self.args['todo'],
                'old_parent': self.args['new_parent'],
                'new_parent': self.args['old_parent']
            }
            return Transaction('move', args)
        elif self.command == 'folder' and self.args['subcommand'] == 'new':
            args = {
                'subcommand': 'delete',
                'folder': self.args['folder'],
                'todos': []
            }
            return Transaction('folder', args)
        elif self.command == 'folder' and self.args['subcommand'] == 'delete':
            args = {
                'subcommand': 'new',
                'folder': self.args['folder'],
                'todos': self.args['todos']
            }
            return Transaction('folder', args)
        elif self.command == 'folder' and self.args['subcommand'] == 'rename':
            args = {
                'subcommand': 'rename',
                'old_folder': self.args['new_folder'],
                'new_folder': self.args['old_folder'],
            }
            return Transaction('folder', args)
