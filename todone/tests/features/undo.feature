Feature: Undo/Redo recent actions

  Background: Assume the database is initialized
    Given an initialized database

  Scenario: Undo on an empty database
    When we run the command "undo"
    Then the output includes "No actions to undo"
    And  the output does not include "initialize the database"

  Scenario: Redo on an empty database
    When we run the command "redo"
    Then the output includes "No undone actions to redo"

  Scenario: Undo a new todo
    Given we ran the command "new My todo"
    And   we ran the command "undo"
    When  we run the command "list My todo"
    Then the output does not include "My todo"

  Scenario: Undo a move command
    Given we ran the command "new My todo"
    And   we ran the command "list My todo"
    And   we ran the command "move 1 today/"
    When  we run the command "undo"
    Then  the output includes "Moved: My todo -> inbox"
