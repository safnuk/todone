Feature: Move todos between folders and projects

  Background: Assume the database is inititalized and contains todo items
    Given an initialized database
    And the database includes each <todo>
      | todo                                     |
      | inbox/New todo                           |
      | next/Another thing todo                  |
      | next/test project                        |
      | [test project] Sub item the first        |
      | today/Sub item the second [next/project] |

  Scenario: Move a todo to a different folder
    Given we ran the command "list inbox/"
    When we run the command "move 1 today/"
    Then the output includes "Moved: New todo -> today"

  Scenario: Move a todo and list the target folder
    Given we ran the command "list inbox/"
    And   we ran the command "move 1 today/"
    When  we run the command "list today/"
    Then  the output includes "New todo"

  Scenario: Move a todo into a project
    Given we ran the command "list inbox/"
    When  we run the command "move 1 [next/project]"
    Then  the output includes "Moved: New todo -> [test project]"

  Scenario: Move a todo into a project and check original folder
    Given we ran the command "list inbox/"
    And   we ran the command "move 1 [next/project]"
    When  we run the command "list inbox/"
    Then  the output includes "New todo"

  Scenario: Move a todo from one project into another
    Given we ran the command "list [project] second"
    When  we run the command "move 1 [New todo]"
    Then the output includes "Moved: Sub item the second -> [New todo]"

  Scenario: Use done command to move a todo into done folder
    Given we ran the command "list today/"
    When  we run the command "done 1"
    Then  the output includes "Moved: Sub item the second -> done/"
