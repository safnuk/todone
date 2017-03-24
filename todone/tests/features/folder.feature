Feature: Change folder structure

  Background: Assume the database is inititalized
    Given an initialized database

  Scenario: Create a todo in a non-existent folder
    When we run the command "new nonfolder/New todo"
    Then the output includes "Invalid argument"
    And  the output includes "No match found for folder nonfolder/"

  Scenario: Create a new folder
    When we run the command "folder new testfolder"
    Then the output includes "Added folder: testfolder/"

  Scenario: Add a todo to an existing non-default folder
    Given we ran the command "folder new testfolder/"
    When  we run the command "new test/New todo"
    Then  the output includes "Added: testfolder/New todo"

  Scenario: Ambiguous pattern match on folders
    Given we ran the command "folder new testfolder"
    And   we ran the command "folder new testfolder1"
    When  we run the command "new test/Another todo"
    Then  the output includes "Invalid argument"
    And   the output includes "Multiple matches found for folder test/"

  Scenario: Exact pattern match on closely named folder
    Given we ran the command "folder new testfolder"
    And   we ran the command "folder new testfolder1"
    When  we run the command "new testfolder/Another todo"
    Then  the output includes "Added: testfolder/Another todo"

  Scenario: Rename a folder should move associated todos
    Given we ran the command "folder new testfolder"
    And   we ran the command "new testfolder/My todo"
    When  we run the command "folder rename testfolder/ myfolder/"
    And   we run the command "list My todo"
    Then  the output includes "Renamed folder: testfolder/ -> myfolder/"
    And   the output includes "myfolder/My todo"

  Scenario: Delete a folder should move associated todos to inbox
    Given we ran the command "folder new testfolder"
    And   we ran the command "new testfolder/My todo"
    When  we run the command "folder delete testfolder/"
    And   we run the command "list inbox/"
    Then  the output includes "Deleted folder: testfolder/"
    And   the output includes "My todo"
