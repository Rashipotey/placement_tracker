Feature: Authentication and RBAC (USER/ADMIN)
  #Jira: CPT-33, CPT-36, CPT-37, CPT-38, CPT-39, CPT-47, CPT-26, CPT-41
  #Confluence: LLD 1441797


  Background:
    Given the Placement Tracker application is running

  @Smoke
  Scenario: User can register and log in and reach USER dashboard
    When I register a new user with a valid email and password
    And I log in with that email and password
    Then I should be navigated to the USER dashboard
    And a JWT token should be stored in localStorage

  Scenario: Protected routes redirect unauthenticated users to login
    When I visit the dashboard page without loggin in
    Then I should be redirected to the login page

  @Regression CPT-47
  Scenario: Login api contract uses JSON body and returns bearer token
    When I log in via the API with valid credentials
    Then the response should contain an access_token and token_type
    And token_type should be "bearer"

  @Regression CPT-33
  Scenario: Invalid token is cleared and user is redirected to login
    Given I have an invalid token in localStorage
    When I visit the dashboard page
    Then I should be redirected to the login page
    And the stored token should be removed

  @CPT-39 CPT-35 @Responsive
  Scenario: USER role lands on /dashboard and cannot see admin actions
    Given I am logged in as a USER
    When I visit the home page
    Then I should be navigated to /dashboard
    And I should not see company management actions

  @CPT-39 CPT-35 @Responsive
  Scenario: ADMIN role lands on /admin company management dashboard
    Given I am logged in as an ADMIN
    When I visit the home page
    Then I should be navigated to /admin
    And I should see company management actions
