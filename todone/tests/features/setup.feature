Feature: Configuration file and database initialization

  Scenario: A help message should be displayed when accessing an unitialized database
    Given an uninitialized database
    When we run the command "new A new todo item"
    Then the output includes "Database not setup properly"

  Scenario: Initializing the database
    Given an uninitialized database
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

  Scenario: Initializing a database with blank config file
    Given an uninitialized database
    When we initialize the database with a blank config file
    Then we are prompted for name of database file to use
    And the output includes "New todone database initialized"
