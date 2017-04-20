Feature: Errors occur during processing

  Background: Assume the database is inititalized and contains todo items
    Given an initialized database
    And the database includes each <todo>
      | todo                                     |
      | inbox/New todo                           |
      | next/Another thing todo                  |
      | next/test project                        |
      | [test project] Sub item the first        |
      | today/Sub item the second [next/project] |

  Scenario: Invalid command specified
    When we run the command "junk inbox/"
    Then the output includes "Invalid argument"
    And  the output includes "help"

