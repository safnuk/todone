Feature: Add new todos

  Background: Assume the database has already been initialized
    Given an initialized database

  Scenario: Add a new todo
    When we run the command "new New todo"
    Then the output includes "inbox/New todo"

  Scenario: Add a todo to the next/ folder
    When we run the command "new next/ Another todo"
    Then the output includes "next/Another todo"

  Scenario: Create a project todo and some sub-items
    Given an existing todo "next/test project"
    When we run the command "new [test project] Sub item the first"
    And we run the command "new to/ Sub item the second [next/project]"
    Then the output includes each <project>
      | project                                  |
      | inbox/Sub item the first [test project]  |
      | today/Sub item the second [test project] |
