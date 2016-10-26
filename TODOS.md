- Add cal folder for calendar items
- Refactor tests using fixtures
- Test and code for multiple project hits with new_todo
- Allow number designators for project tags
- Check for circular project structures
- Improve list_item output
  * Group items by projects
  * Print project as headers
  * Allow specifiying depth of sub-projects to display
  * Display due and reminder dates
  * Use unicode check boxes ☐ ☑ ☒ ◎ ◉  ◯ ❌ ✖ ✕ ✓ ✔  ▷ ► ✅  ▢ ▣
- Implement recurring todos
- Add timers to task "todone timer start/stop #"
  Active timers should be displayed when performing many operations
- Add log command to show todos done over a specified period of time
- Add quick-entry command: "todone quick folder/ [project] @Context"
  Prompt to enter a list of todos (blank line to terminate),
  all of folder, project and context are optional
- Make sure framework can easily implement a "notes" folder
- Move folder properties from config file to db model
- Add folder properties (active/inactive, etc)
- Improve output messages for completed operations

0.1 Roadmap
- setup command should create a basic config file if one is missing/empty
- fix error with setup of empty config not creating db file
- Update classifiers (setup.py)
- Make list help message correct
- Improve move help message
- Add done shorthand command
- Add trash folder
- Add trash shorthand command
- Make max date(9999, 12, 31) into global constant
- Update version number (in code and setup.py)

0.2 Roadmap
-----------
- Use SQL search for FolderMatch
- Record date/time when moving to "done" folder
- Decide when and how to clear DONE and CANCEL items from saved lists
- Decide when and how to clear CANCEL items from database
- Add "context" field to Todo
- Implement due date property
- Implement reminder date property
- Improve output messages for completed operations
- Add agenda command
