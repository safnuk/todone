import datetime


class Transaction:
    def __init__(self, command, args={}, timestamp=None):
        self.command = command
        self.args = args
        self.timestamp = timestamp if timestamp else datetime.datetime.now()
