Feature: List existing todo items

  Background: Assume the database is inititalized and contains todo items
    Given an initialized database
    And the database includes each <todo>
      | todo                                     |
      | inbox/New todo                           |
      | next/Another thing todo                  |
      | next/test project                        |
      | [test project] Sub item the first        |
      | today/Sub item the second [next/project] |

  Scenario: List a folder
    When we run the command "list inbox/"
    Then the output includes "New todo"
    And  the output includes "Sub item the first"
    But  the output does not include "Another thing todo"
    And  the output does not include "Sub item the second"

  Scenario: Use the last-list save feature
    Given we ran the command "list next/"
    When  we run the command "list"
    Then  the output includes "Another thing todo"
    And   the output includes "test project"
    But   the output does not include "New todo"
    And   the output does not include "Sub item"

  Scenario: Use the named saved search feature
    Given we ran the command "list .next next/"
    And   we ran the command "list today/"
    When  we run the command "list .next"
    Then  the output includes "Another thing todo"
    And   the output includes "test project"
    But   the output does not include "New todo"
    And   the output does not include "Sub item"

  Scenario: List todos matching keywords
    When we run the command "list todo"
    Then the output includes "New todo"
    And  the output includes "Another thing todo"
    But  the output does not include "test project"
    And  the output does not include "Sub item" 

  Scenario Outline: List todos by searching for a project
    When we run the command <command>
    Then the output includes "Sub item the first"
    And  the output includes "Sub item the second"
    
  Examples: list commands
    | command               |
    | "list [test project]" |
    | "list [next/project]" |
    | "list [project]"      |
