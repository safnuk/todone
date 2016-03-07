from todone.config import settings


class Todo:

    def __init__(self, action, folder=None, remind_date=None):
        if action:
            self.action = action
        else:
            raise ValueError("Cannot create an empty action item")
        if folder is None:
            self.folder = settings['folders']['default_inbox']
        elif folder in settings['folders']['default_folders']:
            self.folder = folder
        else:
            raise ValueError("Invalid todo type specified")
