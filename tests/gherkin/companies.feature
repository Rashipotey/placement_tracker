Feature: Company management
  #Jira: CPT-5, CPT-34, CPT-38, CPT-40, CPT-45, CPT-46
  #Confluence: LLD 1441797

  Background:
    Given I am logged in

  @CPT-38 CPT-46 @negative
  Scenario: USER cannot create a company via API (403)
    Given I am logged in as a USER
    When I post a company via the API with valid data
    Then the response status should be 403

  @CPT-38
  Scenario: Any authenticated user can list companies via API (200)
    Given I am logged in as a USER
    When I get the company list via the API
    Then the response status should be 200
    And the response should be a JSON array

  @CPT-40 @USI-ADMIN
  Scenario: ADMIN can create, edit, and delete a company in the UI (happy path)
    Given I am logged in as an ADMIN
    When I create a new company in the admin UI with valid fields
    Then The company should appear in the company table
    When I edit the company in the admin UI
    Then The updated values should be visible in the table
    When I delete the company in the admin UI
    Then The company should be removed from the table

  @CPT-34 CPT-38 @negative
  Scenario: Delete company that is referenced by an application returns 409 and shows a user-friendly message in UI
    Given I am logged in as an ADDIN    And a company is referenced by at least one application
    When I attempt to delete that company in the admin UI
    Then I should see a conflict error message
    And the company should remain in the table

  @CPT-45
  Scenario: USER can view the Companies page but it is read-only (no create/edit/delete actions)
    Given I am logged in as a USER
    When I visit the Companies page
    Then I should see a companies table
    And I should not see admin actions for companies
