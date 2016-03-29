- Make max date(9999, 12, 31) into global constant
- Allow arbitrary folder names
- Add cal folder for calendar items
- Decide when and how to clear DONE and CANCEL items from saved lists
- Decide when and how to clear CANCEL items from database
- Refactor tests using fixtures
- Test and code for multiple project hits with new_todo
- Allow number designators for project tags
- Add "context" field to Todo
- Raise error when setting up db with missing config file
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
