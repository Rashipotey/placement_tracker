Feature: Applications ownership and interview rounds
  #Jira: CPT-6, CPT-7, CPT-9, CPT-44, CPT-48
  #Confluence: LLD 1441797

  Background:
    Given I am logged in as a USER

  @CPT-44
  Scenario: User can select a company when creating an application (UI)
    Given at least one company exists
    When I visit the new application page
    Then I should see a company dropdown with at least one option
    When I save an application with a valid company selected
    Then I should be redirected to the dashboard
    And I should see the new application in the list

  @CPT-6 @negative
  Scenario: User cannot access another user's application (API 403/404)
    Given another user has created an application
    When I attempt to get that application via the API
    Then the response status should be 403 or 404

  @CPT-7
  Scenario: User can create, update, and delete interview rounds for their application (UI)
    Given I have an application with a company
    When I open the rounds page for that application
    Then I should see an empty-state message if no rounds exist
    When I create a round with valid data
    Then The round should appear in the list
    When I edit the round status to PASSED
    Then The updated status should be visible
    When I delete the round
    Then The round should be removed

  @Regression
  Scenario: Deleting the current round clears application.round_id (API)
    Given I have an application with one round
    And I set that round as the current round
    When I delete that round
    Then the application round_id should be null
