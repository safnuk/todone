Todone
======

Command-line todo list manager and agenda, inspired by taskwarrior, todo.sh, and some basic features from org-mode. 


Installation
------------

The easiest way to install todone is through PyPi:

    pip install todone

If you prefer, it can be installed by cloning the git repository:

    git clone https://github.com/safnuk/todone.git
    cd todone
    python setup.py install

Basic Setup
-----------

Before using todone, you need to tell it where to store the data. Type

    todone configure

and answer the questions. The default is to create a sqlite database file. Then type

    todone setup

to create the database with sensible defaults. You are now ready to start tracking your todo items!

Usage
-----

To enter a new todo item, type

    todone new This is my todo item

By default, it will put the todo into the inbox/ folder. You can prepend the item with a different folder:

    todone new today/More important todo

List your todos by folder, keyword search, etc.

    todone list todo

    1 - inbox/This is my todo item
    2 - today/More important todo

    todone list today/

    1 - today/More important todo

    todone move 1 done/

    todone list todo

    1 - inbox/This is my todo item

More comprehensive help is available from the command line

    todone help

gives a general overview, while

    todone help list

gives more specific help on the list command.

Most commands can be entered short hand. For example,

    todone new today/My todo
    todone n to/My todo
    todone ne t/ My todo

are all parsed identically by the program.
