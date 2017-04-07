"""Implementation of todone's backend API as a flat directory structure.

In particular, each :class:`Todo`is saved as a separate file, with
:class:`Folder` implemented as a file system folder.
"""
from todone import backend


class Todo:

    def __init__(self, action, folder=None, remind_date=None):
        if action:
            self.action = action
        else:
            raise ValueError("Cannot create an empty action item")
        if folder is None:
            self.folder = backend.DEFAULT_FOLDERS['folders']
        elif folder in backend.DEFAULT_FOLDERS['folders']:
            self.folder = folder
        else:
            raise ValueError("Invalid todo type specified")
