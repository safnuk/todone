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
    When  we run the command "undo"
    Then the output includes "Removed: inbox/My todo"

  Scenario: Undo a move command
    Given we ran the command "new My todo"
    And   we ran the command "list My todo"
    And   we ran the command "move 1 today/"
    When  we run the command "undo"
    Then  the output includes "Moved: My todo -> inbox"

  Scenario: Undo then redo a new todo
    Given we ran the command "new My todo"
    And   we ran the command "undo"
    When  we run the command "redo"
    Then  the output includes "Added: inbox/My todo"

  Scenario: Undo then redo a move command
    Given we ran the command "new project"
    And   we ran the command "new other"
    And   we ran the command "new today/My todo [project]"
    And   we ran the command "list today/"
    And   we ran the command "move 1 [other]"
    And   we ran the command "undo"
    When  we run the command "redo"
    Then  the output includes "Moved: My todo -> [other]"

  Scenario: Undo folder deletion
    Given we ran the command "new today/Todo 1"
    And   we ran the command "new today/Todo 2"
    And   we ran the command "folder delete today"
    When  we run the command "undo"
    Then  the output includes "Added folder: today/"
    And   the output includes "Moved: Todo 1 -> today/"
    And   the output includes "Moved: Todo 2 -> today/"

  Scenario: Undo and redo folder deletion
    Given we ran the command "new today/Todo 1"
    And   we ran the command "new today/Todo 2"
    And   we ran the command "folder delete today"
    And   we ran the command "undo"
    When  we run the command "redo"
    Then  the output includes "Deleted folder: today/"
    And   the output includes "Moved: Todo 1 -> inbox/"
    And   the output includes "Moved: Todo 2 -> inbox/"

  Scenario: Undo done command
    Given we ran the command "new My todo"
    And   we ran the command "list My todo"
    And   we ran the command "done 1"
    When  we run the command "undo"
    Then  the output includes "Moved: My todo -> inbox"

  Scenario: Undo then redo done command
    Given we ran the command "new My todo"
    And   we ran the command "list My todo"
    And   we ran the command "done 1"
    And   we ran the command "undo"
    When  we run the command "redo"
    Then  the output includes "Moved: My todo -> done"
