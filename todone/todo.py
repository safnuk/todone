class Todo:
    INBOX = '_'
    NEXT = '__'
    TODAY = '___'
    REMIND = 'r_'
    DONE = 'x'
    CANCEL = 'xx'
    TYPES = [INBOX, NEXT, TODAY, REMIND, DONE, CANCEL]

    def __init__(self, action, _type=None, remind_date=None):
        if action:
            self.action = action
        else:
            raise ValueError("Cannot create an empty action item")
        if _type is None:
            self._type = self.INBOX
        elif _type in self.TYPES:
            self._type = _type
        else:
            raise ValueError("Invalid todo type specified")
        if _type == self.REMIND:
            if remind_date:
                self.remind_date = remind_date
            else:
                raise ValueError("Reminders need to specify a date")
