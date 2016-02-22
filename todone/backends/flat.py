from todone.backends import folders

class Todo:

    def __init__(self, action, folder=None, remind_date=None):
        if action:
            self.action = action
        else:
            raise ValueError("Cannot create an empty action item")
        if folder is None:
            self.folder = folders.INBOX
        elif folder in folders.FOLDERS:
            self.folder = folder
        else:
            raise ValueError("Invalid todo type specified")
