"""Interface specification for any implementation of the todone backend api."""
ERROR = "Class {} doesn't implement {}"

DEFAULT_FOLDERS = {
    'inbox': 'inbox',  # default location for new todos
    # initial folders created
    'folders': [
        'today', 'next', 'inbox', 'cal',
        'done', 'someday', 'garbage'
    ],
    'active': ['today', 'next', 'inbox'],  # folders searched if none specified
    'inactive': ['done', 'garbage'],  # never searched unless specified
    'cal': ['cal'],  # behavior not yet defined (future plans)
    # current: includes upcoming reminders and due todos from other folders
    # when searching for today/ (behavior may change in future)
    'today': ['today'],
    'trash': ['garbage'],  # folder that is regularly cleared
}


class AbstractFolder:
    """Interface for any implementation of :class:`Folder`."""
    @classmethod
    def new(cls, folder_name):
        """Create a new folder.

        :param folder_name: name of the folder created

        :raises DatabaseError: if :data:`folder_name` already exists
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "new()"))

    @classmethod
    def rename(cls, old_folder_name, new_folder_name):
        """Rename a folder.

        Any todos contained in the folder will still be
        contained in the folder after the rename.

        :param old_folder_name: name of folder to be renames
        :param new_folder_name: new name for the folder

        :raises DatabaseError: if data:`new_folder_name` already exists
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "rename()"))

    @classmethod
    def remove(cls, folder_name):
        """Delete a folder

        Any todos contained in the folder will be moved to ``inbox/``.

        :param folder_name: name of the folder to be deleted

        :raises DatabaseError: if :data:`folder_name` is not a valid
            name of an existing folder
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "remove()"))

    @classmethod
    def all(cls):
        """Retrieve all folders stored in the database.

        :return: iterable of folders
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "all()"))

    @classmethod
    def get_unique_match(cls, prefix):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_unique_match()"))


class AbstractTodo:
    """Interface for any implementation of :class:`Todo`."""
    @classmethod
    def query(cls, **search_parameters):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "query()"))

    @classmethod
    def active_todos(cls):
        """Construct a select query of all active todos. """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "active_todos()"))

    @classmethod
    def get_projects(cls, search_string):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_projects()"))

    @classmethod
    def get_unique_match(cls, **search_parameters):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_unique_match()"))

    @classmethod
    def new(cls, **args):
        """Create a new todo.

        Required keyword argument:
            :param action: title of the todo item

        Optional keyword arguments:
            :param parent: database key to the parent todo (make the todo
                a subitem of a larger project, called the *parent*)
            :param folder: folder to store the todo in (defaults to inbox/)
            :param due: due date of the todo
            :param remind: reminder date for the todo

        :raises DatabaseError: if :data:`action` is the empty string
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "new()"))

    def save(self):
        """Save any updates made to the todo to the database."""
        raise NotImplementedError(
            ERROR.format(self.__class__.__name__, "save()"))


class AbstractSavedList:
    """Interface for any implementation of :class:`SavedList`."""
    @classmethod
    def get_most_recent(cls):
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_most_recent()"))

    @classmethod
    def get_todos_in_list(cls, listname):
        """Return the todos contained in a saved list.

        :param listname: the name of the saved list as stored in db

        :returns: iterable of todo items contained in the saved list

        :raises DatabaseError: if listname is not a valid name for a
            :class:`SavedList`
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get_todos_in_list()"))

    @classmethod
    def get_todos_from_most_recent_search(cls):
        """Return the todos from the most recent list query.

        :returns: iterable of todo items that appeared in most recent
            invocation of :func:`list_todos`
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__,
                         "get_todos_from_most_recent_search()"))

    @classmethod
    def save_search(cls, name, todo_query):
        """Save a list of todos for future queries.

        :param name: the name of the saved search
        :param todo_query: list of todos to be saved
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "save_search()"))

    @classmethod
    def save_most_recent_search(cls, todo_query):
        """Save a list of todos under the default :class:`SavedList`.

        :param todo_query: list of todos to be saved
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "save_most_recent_search()"))


class AbstractDatabase:
    """Interface for any implementation of :class:`Database`."""
    @classmethod
    def create(cls):
        """Create the database tables.

        Populate the Folders table with default folders
        (inbox, today, next, etc.)

        :raises DatabaseError: if the database has already been created
            or an error occured during the creation process
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "create()"))

    @classmethod
    def connect(cls):
        """Open a connection to the database.

        :raises DatabaseError: if connection attempt fails
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "connect()"))

    @classmethod
    def close(cls):
        """Close the database connection."""
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "close()"))

    @classmethod
    def update(cls):
        """Close any existing connections and reopen the database.

        Call after changing :data:`config.settings` to ensure the
        database connection refers to the database specified.
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "update()"))


class AbstractCommandStack:
    """Store the history of commands performed on the database"""
    @classmethod
    def push(cls, command):
        """Add command to the front of the stack."""
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "push()"))

    @classmethod
    def pop(cls):
        """Get the command at position index.

        index is an integer, giving the position relative base 1. I.e.
        index=1 is the top (most recent) command on the stack.

        returns the Command at position index
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "get()"))

    @classmethod
    def list(cls, range=10):
        """Get a list of recent commands.

        range is an integer specifying how many Commands to return.

        returns a list of the range most recent commands.
        """
        raise NotImplementedError(
            ERROR.format(cls.__class__.__name__, "list()"))
