import datetime


class Transaction:
    def __init__(self, command, args={}, timestamp=datetime.datetime.now()):
        self.command = command
        self.args = args
        self.timestamp = timestamp
