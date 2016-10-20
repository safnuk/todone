- Make max date(9999, 12, 31) into global constant
- Allow arbitrary folder names
- Add cal folder for calendar items
- Decide when and how to clear DONE and CANCEL items from saved lists
- Decide when and how to clear CANCEL items from database
- Refactor tests using fixtures
- Test and code for multiple project hits with new_todo
- Allow number designators for project tags
- Add "context" field to Todo
- Check for circular project structures
- Improve list_item output
  * Group items by projects
  * Print project as headers
  * Allow specifiying depth of sub-projects to display
  * Display due and reminder dates
  * Use unicode check boxes ☐ ☑ ☒ ◎ ◉  ◯ ❌ ✖ ✕ ✓ ✔  ▷ ► ✅  ▢ ▣
- Record date/time when moving to "done" folder
- Implement recurring todos
- Use SQL search for FolderMatch
- Add timers to task "todone timer start/stop #"
  Active timers should be displayed when performing many operations
- Add log command to show todos done over a specified period of time
- Add quick-entry command: "todone quick folder/ [project] @Context"
  Prompt to enter a list of todos (blank line to terminate),
  all of folder, project and context are optional
- Make sure framework can easily implement a "notes" folder

0.1 Roadmap
===========
- Add configure command (creates config.ini file with user defined db)
- setup command should raise an error when run with empty/missing config file
- Move folder properties from config file to db model
- Improve output messages for completed operations
- Improve README file
- Make sure license is acceptable
- Update classifiers (setup.py)
- Add folder and move commands to help message
- Add folder rename and folder delete commands
- Make list help message correct
- Improve move help message
- Add folder properties (active/inactive, etc)
- Add done shorthand command
- Update version number (in code and setup.py)
