Feature: Configuration file and database initialization

  Scenario: A help message should be displayed when accessing an unitialized database
    Given an unitialized database
    When we add a new todo item
    Then the output includes "Cannot find valid database"

  Scenario: Initializing the database

    Given an unitialized database
    When we initialize the database
    And we list the folders
    Then the output includes "New todone database initialized"
    And the output includes each <folder>
        | folder |
        | inbox  |
        | today  |
        | done   |
        | next   |


  Scenario: Initializing an existing database
    Given an initialized database
    When we initialize the database
    Then the output includes "Database has already been setup"
