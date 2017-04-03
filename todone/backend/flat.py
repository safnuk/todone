from todone.backend import DEFAULT_FOLDERS


class Todo:

    def __init__(self, action, folder=None, remind_date=None):
        if action:
            self.action = action
        else:
            raise ValueError("Cannot create an empty action item")
        if folder is None:
            self.folder = DEFAULT_FOLDERS['folders']
        elif folder in DEFAULT_FOLDERS['folders']:
            self.folder = folder
        else:
            raise ValueError("Invalid todo type specified")
