Feature: Configuration file and database initialization

  Scenario: A help message should be displayed when accessing an unitialized database
    Given an unitialized database
    When we run the command "new A new todo item"
    Then the output includes "Database not setup properly"

  Scenario: Initializing the database

    Given an unitialized database
    When we run the command "setup init"
    And we run the command "folder list"
    Then the output includes "New todone database initialized"
    And the output includes each <folder>
        | folder |
        | inbox  |
        | today  |
        | done   |
        | next   |


  Scenario: Initializing an existing database
    Given an initialized database
    When we run the command "setup init"
    Then the output includes "Database has already been setup"
