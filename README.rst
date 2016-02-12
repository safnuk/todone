Todone
======

Todo list manager and agenda, inspired by taskwarrior, todo.sh, and some basic features from org-mode. 

Commands
--------

new [project]
show
list
move
edit
tag
done

change?

Fields
------

_type in [INBOX, NEXT, TODAY, REMIND, DONE, CANCEL]
    (use REMIND for calendar entries??)
action / item / title
repeat
tags
remind date
due date
notes
date completed
project

Prefixes
--------

_  [+N{d,w,m,y}] inbox (with optional repeat)
__  next
___ today
r YYYY-MM-DD[+N{d,w,m,y}] reminder (with optional repeat)
x YYYY-MM-DD  done
xx  cancel
