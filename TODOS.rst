0.1 Roadmap
-----------

* Add missing api documentation
* Convert all argparsers to use ``ParserFactory`` class
* Update classifiers (setup.py)
* Update version number (in code)

0.2 Roadmap
-----------

* Implement undo/redo operation
* Implement REST interface
* Implement local/master sync
* Improve project matching logic
* Separate console output to a different module
* Use SQL search for FolderMatch
* Record date/time when moving to "done" folder
* Decide when and how to clear DONE and TRASH items from saved lists
* Improve output messages for completed operations
* Add trash shorthand command

Future
------

* Move bulk of config details into db table
* Decide when and how to clear TRASH items from database
* Add agenda command
* Add "context" field to Todo
* Make max ``date(9999, 12, 31)`` into global constant
* Implement due date property
* Implement reminder date property
* Add cal folder for calendar items
* Refactor tests using fixtures
* Test and code for multiple project hits with new_todo
* Allow number designators for project tags
* Check for circular project structures
* Improve list_item output

  * Group items by projects
  * Print project as headers
  * Allow specifiying depth of sub*projects to display
  * Display due and reminder dates
  * Use unicode check boxes ☐ ☑ ☒ ◎ ◉ ◯❌✖ ✕ ✓ ✔  ▷ ► ✅ ▢ ▣

* Implement recurring todos
* Add timers to task ``todone timer start/stop #``
  Active timers should be displayed when performing many operations
* Add log command to show todos done over a specified period of time
* Add quick-entry command: ``todone quick folder/ [project] @Context``
  Prompt to enter a list of todos (blank line to terminate),
  all of folder, project and context are optional
* Make sure framework can easily implement a "notes" folder
* Move folder properties from config file to db model
* Add folder properties (active/inactive, etc)
* Improve output messages for completed operations
