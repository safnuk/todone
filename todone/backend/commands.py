import textwrap

from todone import backend
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
        print(cls.response)
        return cls.response

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
            cls.response = cls.db_help_msg.format(e)
        return super().run()


class NoDB(AbstractDispatch):
    @classmethod
    def run(cls, args):
        cls.response = cls._implement(args)
        return super().run()


class Done(InitDB):
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
    commands = ['new', 'rename', 'delete', 'list']
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
    def dispatch(cls, command):
        return {
            'new': cls._new,
            'rename': cls._rename,
            'delete': cls._delete,
            'list': cls._list,
        }[command]

    @classmethod
    def _new(cls, *folders):
        backend.Folder.new(*folders)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['new'].format(*folders)
        )

    @classmethod
    def _rename(cls, *folders):
        backend.Folder.rename(*folders)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['rename'].format(*folders)
        )

    @classmethod
    def _delete(cls, *folders):
        backend.Folder.remove(*folders)
        return response.Response(
            response.Response.SUCCESS,
            cls.message['delete'].format(*folders)
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
        try:
            return cls.dispatch(command)(*folders)
        except exceptions.ArgumentError as e:
            return response.Response(response.Response.ERROR,
                                     str(e))


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

    Allowed commands include: help, list, new, setup, version.

    Type "todone help <command>" to read more about a specific command.
    """
    short_help = """
    usage todone help [command]

    Allowed commands include: help, list, new, setup, version.
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


class Move(InitDB):
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
        status = response.Response.SUCCESS
        todos = backend.SavedList.get_todos_from_most_recent_search()
        if len(todos) < args['index']:
            status = response.Response.ERROR
            msg = 'Index {} out of range'.format(args['index'])
            return response.Response(status, msg)
        target = todos[args['index']-1]
        if args.get('folder'):
            target.folder = utils.match_folder(args['folder'])
            msg = 'Moved: {} -> {}/'.format(target.action, target.folder.name)
        elif args.get('parent'):
            target.parent = utils.match_parent(**args['parent'])
            msg = 'Moved: {} -> [{}]'.format(
                target.action, target.parent.action)
        target.save()
        return response.Response(status, msg)


class New(InitDB):
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
            if args.get('folder'):
                args['folder'] = utils.match_folder(args['folder'])
            else:
                args['folder'] = backend.DEFAULT_FOLDERS['inbox']
            if args.get('parent'):
                args['parent'] = utils.match_parent(
                    **args['parent'])
            backend.Todo.new(**args)
            msg = 'Added: {}/{}'.format(args['folder'], args['action'])
            if args.get('parent'):
                msg += ' [{}]'.format(args['parent'].action)
            return response.Response(response.Response.SUCCESS, msg)
        except exceptions.ArgumentError as e:
            return response.Response(response.Response.ERROR, str(e))


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
        return name if name else cls.DEFAULT_DB

    @classmethod
    def get_input(cls):
        query = "Enter location of database ['{}']: ".format(cls.DEFAULT_DB)
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
        return ('error', args['message'])


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
}
