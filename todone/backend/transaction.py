import datetime


class Transaction:
    def __init__(self, command, args={}, timestamp=None, client=None):
        self.command = command
        self.args = args
        self.timestamp = timestamp if timestamp else datetime.datetime.now()
        self.client = client

    def __str__(self):
        return '({}, {})'.format(self.command, self.args)

    def __repr__(self):
        return 'Transaction{}'.format(self.__str__())

    def inverse(self):
        if self.command == 'new':
            return Transaction('remove', self.args)
        elif self.command == 'remove':
            return Transaction('new', self.args)
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
            todos = [Transaction('move', args) for args in self.args['todos']]
            args = {
                'subcommand': 'delete',
                'folders': self.args['folders'],
                'todos': [todo.inverse().args for todo in todos]
            }
            return Transaction('folder', args)
        elif self.command == 'folder' and self.args['subcommand'] == 'delete':
            todos = [Transaction('move', args) for args in self.args['todos']]
            args = {
                'subcommand': 'new',
                'folders': self.args['folders'],
                'todos': [todo.inverse().args for todo in todos]
            }
            return Transaction('folder', args)
        elif self.command == 'folder' and self.args['subcommand'] == 'rename':
            folders = self.args['folders']
            args = {
                'subcommand': 'rename',
                'folders': [folders[1], folders[0]]
            }
            return Transaction('folder', args)
