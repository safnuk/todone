Commands
========

Todone is accessed through its command line interface.
The available commands include
``new``, ``move``, ``list``, ``folder``, ``done``, ``help``, and ``setup``,
each of which are explained below.

In general, any command can be entered in an abbreviated form, provided
it has a unique completion. For example,

However, where possible, todone
allows abbreviated versions of each of the above command, provided that
what you type can be uniquely expanded to one of the valid command names.

done
----

Move a todo from most recent search to the done folder.

Usage: 

.. code-block:: console

    $ todone done <N>

The index ``N`` refers to the position of the todo listed in
the most recent search.

folder
------

Edit the folder structure of the todo list.

Usage: 

.. code-block:: console

    $ todone folder new <foldername>

creates a new folder.

.. code-block:: console

    $ todone folder delete <foldername>

deletes the given folder. Any todo items contained in the
deleted folder will be automatically moved to ``inbox/``.

.. code-block:: console

    $ todone folder list

prints a list of all current folder names.

.. code-block:: console

    $ todone folder rename <old folder name> <new folder name>

renames a folder.

help
----

Obtain help from the command line.

Usage:

.. code-block:: console

    $ todone help

for general instructions.

.. code-block:: console

    $ todone help <command>

for help on a specific command.

list
----

Print a list of todos matching given search terms.

Usage:

.. code-block:: console

    $ todone list [.<file>] [<folder>/] [tags and keywords]

Search criteria can be any string expression.

Allowed ``folder`` keywords are any valid folder name, followed by
a slash. Default folders created include ``today/``, ``next/``,
``inbox/``, ``someday/``, ``done/``, and ``garbage/``.
Shortened versions accepted when unambiguous, so,
for example ``done/``, ``don/``, ``do/``, and ``d/`` all
indicate the ``done/`` folder.

If the folder is not specified, the search is over all active
folders (default is: ``inbox/``, ``next/``, ``today/``).

Allowed tags are:

    * ``due[+<N>{d|w|m|y}]``    find all todos due within the specified timeframe
    * ``remind[+<N>{d|w|m|y}]`` find all todos with an upcoming reminder
    * ``[project name]``        find all sub-items of the todo item ``project name``.
      Here the square brackets are a necessary part of the notation, not an 
      indication of an optional field.

The remainder of the search string provides keywords that must
appear in the todo title. However, searches are always case
insensitive.

If ``.file`` is specified, then search results are saved for future reference.

If no search criteria is provided, then the todos in the given ``file``
are listed. If no search criteria and no file is specified, then
the most recently run search is listed.

:Examples:

.. code-block:: console

    $ todone list .my_search today/ @Work

Lists all items in the ``today/`` folder containing tag @Work,
and saves to ``.my_search``.

.. code-block:: console

    $ todone list n/due+1w [My Project]

Lists all ``next/`` items from project ``My Project`` due in the next week.

.. code-block:: console

    $ todone list

Repeats most recent search.

.. code-block:: console

    $ todone list .my_search

Repeats list from first search.

move
----

Move a todo from the most recent search to a new folder or project.

Usage:

.. code-block:: console

    $ todone move <N> <folder>/

    $ todone move <N> [<project>]

The index ``N`` refers to the position of the todo listed in
the most recent search.

:Examples:

.. code-block:: console

    $ todone list todo
    1 - inbox/First thing todo
    2 - today/Another thing todo

    $ todone move 1 next/
    Moved: First thing todo -> next/

    $ todone move 1 [projects/My great project]
    Moved: First thing todo -> [My great project]

    $ todone list todo
    1 - today/Another thing todo
    [My great project]
    2 - next/First thing todo

new
---

Create a todo item.

Usage:

.. code-block:: console

    $ todone new [<folder>/] [tags and todo title]

creates a new todo with the given title.

The todo is created in ``folder/``, which can be any valid folder name,
followed by a slash.  One can instead enter a partial match, provided
it has a unique completion. If no ``folder/`` is specified, the
todo is put into ``inbox/`` by default.

The todo title can be any text string.

Allowed tags are:

    * ``due[+<N>{d|w|m|y} | <YYYY>-<MM>-<DD>]``
    * ``remind[+<N>{d|w|m|y} | <YYYY>-<MM>-<DD>][+<N>{d|w|m|y}]``
    * ``[<Project name>]``

Entering ``remind+<N>{d|w|m|y}+<N>{d|w|m|y}`` sets up a
recurring reminder. For example,

.. code-block:: console

    $ todone new My recurring todo r+7d+1m

sets up a reminder for 7 days from now, with a new reminder created
1 month after completion (ad nauseum).

Using keyword ``[<Project name>]`` places the todo as a sub-item
of the todo identified through ``Project name``. A search if performed
for partial matches to todos with the given title. You can also include the
folder to narrow down the search even further.

It is recommended that you create a ``projects/`` folder for placing
any todo item that breaks down into multiple steps (aka, a *project*).
Then, it is easy to refer to any of your projects by entering
``[p/My great project]``.

The title used for the todo consists of the argument string remaining
after removing all valid tags.

setup
-----

Create a basic configuration file (if needed), based on user input, and
initializes a new, empty database (if one does not exist).

Usage:

.. code-block:: console

    $ todone setup init
