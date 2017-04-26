import textwrap

from todone import backend
from todone.backend import transaction as trans
from todone.backend import utils
from todone import config
from todone import exceptions
from todone import response
from todone import __version__


class AbstractDispatch:
    response = {}
    long_help = ''
    short_help = ''

    @classmethod
    def run(cls, args=None):
        raise NotImplementedError("Method run() not implemented")

    @classmethod
    def _implement(cls, args):
        raise NotImplementedError("Method _implement() not implemented")


class InitDB(AbstractDispatch):
    db_help_msg = """{}

    Enter
        > todone setup init
    to create a basic config file and initialize the database.
    """

    @classmethod
    def run(cls, args):
        try:
            backend.Database.connect()
            cls.response = cls._implement(args)
            backend.Database.close()
        except backend.DatabaseError as e:
            cls.response = response.Response(
                response.Response.ERROR, cls.db_help_msg.format(e))
        return cls.response


class NoDB(AbstractDispatch):
    @classmethod
    def run(cls, args):
        cls.response = cls._implement(args)
        return cls.response


class SyncCommand():
    @classmethod
    def apply(cls, transaction, stacks):
        raise NotImplementedError("Method apply() not implemented")


class Done(NoDB):
    """Move a todo into the done folder"""

    long_help = """
    Move a todo from most recent search to the done folder.

    usage: todone done N

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    short_help = """
    usage: todone done N

    where N is the number of the todo referenced in most recent search.
    """

    @classmethod
    def _implement(cls, args):
        move_args = dict(args)
        move_args.update({'folder': 'done'})
        return Move.run(move_args)


class Folder(InitDB):
    """Class containing commands for modifying folders in todone database.

    Includes the subcommands:
        * ``new`` for creating new folders
        * ``rename`` for renaming a folder
        * ``delete`` for deleting a folder
    """

    long_help = """
        Edit the folder structure of the todo list.

        usage: todone folder <command> <folder(s)>

        Valid commands are:

            new    create a new folder with the given name
            rename rename an existing folder
            delete remove a folder
            list   list all folders
        """
    short_help = """
        usage todone folder <command> <args>
        """
    message = {
        'new': 'Added folder: {}/',
        'rename': 'Renamed folder: {}/ -> {}/',
        'delete': 'Deleted folder: {}/',
        'list': '',
    }
    min_folders = {
        'new': 1,
        'rename': 2,
        'delete': 1,
        'list': 0,
    }
    max_folders = {
        'new': 1,
        'rename': 2,
        'delete': 1,
        'list': 0,
    }

    @classmethod
    def _new(cls, folder):
        backend.Folder.new(folder)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['new'].format(folder)
        )

    @classmethod
    def _rename(cls, *folders):
        backend.Folder.rename(*folders)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['rename'].format(*folders)
        )

    @classmethod
    def _delete(cls, folder):
        backend.Folder.remove(folder)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['delete'].format(folder)
        )

    @classmethod
    def _list(cls, *folders):
        folder_names = ['{}/'.format(f.name) for f in backend.Folder.all()]
        return response.Response(
            response.Response.FOLDER_QUERY,
            folder_names
        )

    @classmethod
    def _implement(cls, args):
        command = args.get('subcommand')
        folders = args.get('folders', [])
        if len(folders) < cls.min_folders[command]:
            return response.Response(
                response.Response.ERROR,
                'Not enough folders provided (expected {})'.format(
                    cls.min_folders[command]
                )
            )
        elif len(folders) > cls.max_folders[command]:
            return response.Response(
                response.Response.ERROR,
                'Too many folders provided'
            )
        transaction = cls._build_transaction(command, folders)
        if command in ['new', 'delete', 'rename']:
            stacks = [backend.UndoStack, backend.UnsyncedQueue]
        else:
            stacks = []
        try:
            return cls.apply(transaction, stacks)
        except exceptions.ArgumentError as e:
            return response.Response(response.Response.ERROR,
                                     str(e))

    @classmethod
    def _build_transaction(cls, subcommand, folders):
        if subcommand == 'delete':
            todos = backend.Todo.query(folder=folders[0])
            todo_transactions = [
                Move._build_transaction(
                    todo,
                    {'folder': backend.DEFAULT_FOLDERS['inbox']}).args
                for todo in todos
            ]
        else:
            todo_transactions = []
        args = {'subcommand': subcommand,
                'folders': folders,
                'todos': todo_transactions}
        return trans.Transaction('folder', args)

    @classmethod
    def apply(cls, transaction, stacks=[]):
        responses = []
        args = transaction.args
        command = args['subcommand']
        folders = args['folders']
        todo_transactions = [trans.Transaction('move', todo)
                             for todo in args['todos']]
        if command == 'new':
            responses.append(cls._new(*folders))
            for todo in todo_transactions:
                responses.append(Move.apply(todo))
        elif command == 'delete':
            for todo in todo_transactions:
                responses.append(Move.apply(todo))
            responses.append(cls._delete(*folders))
        elif command == 'rename':
            responses.append(cls._rename(*folders))
        elif command == 'list':
            responses.append(cls._list(*folders))
        else:
            raise NotImplementedError('Folder command {} does not exist'
                                      .format(command))
        for stack in stacks:
            stack.push(transaction)
        return responses


class Help(NoDB):
    """Display help messages for todone commands."""

    long_help = """
    Command-line agenda and todo-list manager.

    usage: todone <command> [<args>]

    Allowed commands include:
        done        Move a todo to the done/ folder
        folder      Commands for manipulating folders (new, rename, delete)
        help        Display this help message
        list        Print a list of todos matching given search terms
        move        Move a todo to a new folder or project
        new         Add a new todo item
        setup       Create config file and initialize database
        version     Display version number

    See todone help <command> to read more about a specific command.
    """
    short_general_help = """
    usage: todone <command> [args]

    Allowed commands include: done, folder, help, list, move, new, setup,
                              version.

    Type "todone help <command>" to read more about a specific command.
    """
    short_help = """
    usage todone help [command]

    Allowed commands include: done, folder, help, list, move, new, setup,
                              version.
    """

    @classmethod
    def _implement(cls, args):
        command = args.get('subcommand')
        if args.get('short'):
            if command:
                msg = COMMAND_MAPPING[command].short_help
            else:
                msg = cls.short_general_help
        else:
            command = command if command else 'help'
            msg = COMMAND_MAPPING[command].long_help
        return response.Response(response.Response.SUCCESS,
                                 textwrap.dedent(msg))


class List(InitDB):
    """Search the database based on user-supplied queries, and
    display the result to the user.
    """

    long_help = """
    Print a list of todos matching given search terms.

    usage: todone list [.file] [folder/] [tags and keywords]

    Search criteria can be any string expression.

    Allowed folder keywords are any valid folder name, followed by
    a slash. Examples: today/, next/, inbox/, someday/, done/. Shortened
    versions accepted when unambiguous, so, for example "done/", "don/",
    "do/", and "d/" all indicate the done folder.

    If folder is not specified, the search is over all active
    folders (default is: inbox/, next/, today/).

    Allowed tags are:

    due[+N{d|w|m|y}],
    remind[+N{d|w|m|y}],
    [project name]

    The remainder of the search string provides keywords that must
    appear in the todo title. However, searches are always case
    insensitive.

    If .file is specified, then search results are saved to .file.

    If no search criteria is provided, then the todos in the given file
    are listed. If no search criteria and no file is specified, then
    the most recently run search is listed.

    E.g.,
        > todone list .my_search today/ @Work
            Lists all today items containing tag @Work, and saves to .my_search
        > todone list n/due+1w [My Project]
            Lists all next items from project [My Project] due in
            the next week
        > todone list
            Repeats most recent search
        > todone list .my_search
            Repeats list from first search
        > todone list
            Repeats list from first search
    """
    short_help = """
    usage: todone list [.file] [folder/] [tags and keywords]
    """

    @classmethod
    def _implement(cls, args):
        if cls.is_loading_saved_search(args):
            query = backend.SavedList.get_todos_in_list(args.get('file'))
        else:
            if args.get('folder'):
                args['folder'] = utils.match_folder(
                    args['folder'])
            if args.get('parent'):
                args['parent'] = backend.Todo.query(**args['parent'])
            query = backend.Todo.query(**args)
            backend.SavedList.save_search(args.get('file'), query)
        backend.SavedList.save_most_recent_search(query)
        return response.Response(
            response.Response.TODO_QUERY,
            query
        )

    @classmethod
    def is_loading_saved_search(cls, args):
        for key, value in args.items():
            if (key != 'file') and value:
                return False
        return True


class Move(SyncCommand, InitDB):
    """Move a todo to a different folder or project. """

    long_help = """
    Move a todo from most recent search to a new folder or project.

    usage: todone move N folder/
           todone move N [project]

    The index N refers to the position of the todo listed in
    the most recent search.
    """
    short_help = """
    usage: todone move N folder/
        todone move N [project]
    where N is the number of the todo referenced in most recent search.
    """

    @classmethod
    def _implement(cls, args):
        todos = backend.SavedList.get_todos_from_most_recent_search()
        if len(todos) < args['index']:
            msg = 'Index {} out of range'.format(args['index'])
            return response.Response(response.Response.ERROR, msg)
        target = todos[args['index']-1]
        transaction = cls._build_transaction(target, args)
        return cls.apply(transaction,
                         [backend.UndoStack, backend.UnsyncedQueue])

    @classmethod
    def apply(cls, transaction, stacks=[]):
        args = transaction.args
        target = backend.Todo.get_by_key(args['todo'])
        if args.get('new_folder'):
            target.folder = args['new_folder']
            msg = 'Moved: {} -> {}/'.format(target.action, target.folder.name)
        elif 'new_parent' in args:
            target.parent = args['new_parent']
            parent_action = target.parent.action if target.parent else ''
            msg = 'Moved: {} -> [{}]'.format(
                target.action, parent_action)
        target.save()
        for stack in stacks:
            stack.push(transaction)
        return response.Response(response.Response.SUCCESS, msg)

    @classmethod
    def _build_transaction(cls, todo, args):
        saved_args = {'todo': todo.id}
        if args.get('folder'):
            saved_args['old_folder'] = todo.folder.name
            saved_args['new_folder'] = utils.match_folder(args['folder'])
        elif args.get('parent'):
            saved_args['old_parent'] = todo.parent.id if todo.parent else None
            new_parent = utils.match_parent(**args['parent'])
            saved_args['new_parent'] = new_parent.id if new_parent else None
        return trans.Transaction('move', saved_args)


class New(SyncCommand, InitDB):
    """Create a new todo."""

    long_help = """
    Create one or more todo items or projects.

    usage: todone new [folder/] [tags and todo string]

    Create new todo the given title.

    Allowed folder names include:
        inbox, next, today, project, someday
    Use the 'folder list' to see all available folders.
    Partial matches are also allowed. The todo is created in the
    given folder, if provided, otherwise it defaults to INBOX.

    The todo title can be any text string, but should be unique.

    Allowed tags are:

    due[+N{d|w|m|y} | YYYY-MM-DD]
    remind[+N{d|w|m|y} | YYYY-MM-DD][+N{d|w|m|y}]
    [Project name]

    Notation remind+N{d|w|m|y}+N{d|w|m|y} sets up a recurring reminder. e.g.
        r+7d+1m
    sets up a reminder for 7 days from now, with a new reminder created
    1 month after completion (ad nauseum).

    The title used for the todo consists of the argument string remaining
    after removing all valid tags.
    """
    short_help = """
    usage: todone new [folder/] [tags and todo string]
    """

    @classmethod
    def _implement(cls, args):
        try:
            transaction = cls._build_transaction(args)
            return cls.apply(
                transaction, [backend.UndoStack, backend.UnsyncedQueue])
        except exceptions.ArgumentError as e:
            return response.Response(response.Response.ERROR, str(e))

    @classmethod
    def apply(cls, transaction, stacks=[]):
        backend.Todo.new(**transaction.args)
        for stack in stacks:
            stack.push(transaction)
        args = transaction.args
        msg = 'Added: {}/{}'.format(args['folder'], args['action'])
        if args.get('parent'):
            parent = backend.Todo.get_by_key(args['parent'])
            msg += ' [{}]'.format(parent.action)
        return response.Response(response.Response.SUCCESS, msg)

    @classmethod
    def _build_transaction(self, args):
        args = dict(args)
        if args.get('folder'):
            args['folder'] = utils.match_folder(args['folder'])
        else:
            args['folder'] = backend.DEFAULT_FOLDERS['inbox']
        if args.get('parent'):
            args['parent'] = utils.match_parent(
                **args['parent']).id
        args['id'] = backend.Todo.get_next_id()
        return trans.Transaction('new', args)


class Setup(NoDB):
    """Create a configuration file (if necessary) and initialize
    the database.
    """

    long_help = """
    Create a basic configuration file (if needed), based on user input, and
    initializes a new, empty database (if one does not exist).

    usage: todone setup init
    """
    short_help = """
    usage: todone setup init
    """

    default_db = '~/.todone.sqlite'
    messages = []

    @classmethod
    def dispatch(cls, subcommand, args=[]):
        cls.subcommands()[subcommand](*args)

    @classmethod
    def subcommands(cls):
        return {'init': cls.initialize}

    @classmethod
    def initialize(cls):
        cls.messages = []
        cls.status = response.Response.SUCCESS
        if not config.settings['database']['name']:
            config.settings['database']['name'] = cls.query_user_for_db_name()
            config.save_configuration()
            backend.Database.update()
            cls.messages.append(
                "Created basic config file '{}'".format(config.config_file))
        try:
            backend.Database.create()
            cls.messages.append(
                "New todone database initialized at '{}'"
                .format(config.settings['database']['name']))
        except backend.DatabaseError as e:
            if "already exists" in str(e):
                cls.messages.append(
                    'Database has already been setup - get working!')
            else:
                cls.status = response.Response.ERROR
                cls.messages.append(str(e))

    @classmethod
    def query_user_for_db_name(cls):
        name = cls.get_input()
        return name if name else cls.default_db

    @classmethod
    def get_input(cls):
        query = "Enter location of database ['{}']: ".format(cls.default_db)
        return input(query).strip()

    @classmethod
    def _implement(cls, args):
        command = args['subcommand']
        cls.dispatch(command)
        return response.Response(cls.status, '\n'.join(cls.messages))


class Version(NoDB):
    long_help = """
        Display version information.

        usage: todone version

        Note that "todone -v" and "todone --version" are also acceptable.
        """
    short_help = """
        usage: todone version
        """

    @classmethod
    def _implement(cls, args):
        if not args:
            return response.Response(
                response.Response.SUCCESS,
                'Todone {}'.format(__version__)
            )
        else:
            return response.Response(
                response.Response.ERROR,
                'version command takes no arguments'
            )


class Configure(NoDB):
    """Setup program-wide configuration settings.

    Uses either the configuration filename parsed from :attr:`args`,
    or, if missing, the default config behavior of :mod:`config`.
    """
    long_help = 'Something is wrong - could not load configuration.'
    short_help = long_help

    @classmethod
    def _implement(cls, args):
        config.configure(args['file'])
        return response.Response(response.Response.NOOP, '')


class Error(NoDB):
    """Reflect error message back to dispatcher."""
    long_help = 'An error occured'
    short_help = 'An error occured'

    @classmethod
    def _implement(cls, args):
        return response.Response(response.Response.ERROR, args['message'])


class Undo(InitDB):
    """
    Pull most recent command off the UndoStack and apply its inverse to the db.
    """
    long_help = """
    Undo the most recent action.

    usage: todone undo
    """
    short_help = """
    usage: todone undo
    """

    @classmethod
    def _implement(cls, args):
        try:
            transaction = backend.UndoStack.pop()
            inverse = transaction.inverse()
            cmd_class = COMMAND_MAPPING[inverse.command]
            backend.RedoStack.push(transaction)
            return cmd_class.apply(inverse, [backend.UnsyncedQueue])
        except exceptions.DatabaseError as e:
            if 'No actions to undo' in str(e):
                return response.Response(
                    response.Response.SUCCESS, str(e)
                )
            raise e


class Redo(InitDB):
    """
    Pull the most recently undone action off the RedoStack and apply it
    to the db.
    """
    long_help = """
    Redo the most recently undone action.

    usage: todone redo
    """
    short_help = """
    usage: todone redo
    """

    @classmethod
    def _implement(cls, args):
        try:
            transaction = backend.RedoStack.pop()
            cmd_class = COMMAND_MAPPING[transaction.command]
            return cmd_class.apply(
                transaction, [backend.UndoStack, backend.UnsyncedQueue])
        except exceptions.DatabaseError as e:
            if 'No undone actions to redo' in str(e):
                return response.Response(
                    response.Response.SUCCESS, str(e)
                )
            raise e


class Remove(InitDB):
    long_help = """
    Remove an item.
    """
    short_help = long_help

    @classmethod
    def _implement(cls, args):
        raise NotImplementedError("Remove command not implemented")

    @classmethod
    def apply(cls, transaction, stacks):
        try:
            args = transaction.args
            backend.Todo.remove(args['id'])
            for stack in stacks:
                stack.push(transaction)
            msg = 'Removed: {}/{}'.format(args['folder'], args['action'])
            return response.Response(response.Response.SUCCESS, msg)
        except exceptions.DatabaseError as e:
            return response.Response(response.Response.ERROR, str(e))


COMMAND_MAPPING = {
    '-h': Help,
    '--help': Help,
    'help': Help,
    '-v': Version,
    '--version': Version,
    'version': Version,
    'folder': Folder,
    'list': List,
    'move': Move,
    'new': New,
    'setup': Setup,
    'done': Done,
    'configure': Configure,
    'error': Error,
    'undo': Undo,
    'redo': Redo,
    'remove': Remove,
}
