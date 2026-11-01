Feature: Input validation, empty/states, and error handling
  #Jira: CPT-41
  #Confluence: UI Wireframes 1572885, LLD 1441797

  @Smoke
  Scenario: Login form validation and error messages
    When I visit the login page
    And I submit without email
    Then I should see an error message "Email is required"
    When I log in with an invalid password
    Then I should see an error message "Invalid email or password"

  Scenario: Registration validation and duplicate email handling
    When I visit the register page
    And I submit without email
    Then I should see an error message "Email is required"
    When I enter a password shorter than 8 characters
    Then I should see an error message "Password must be at least 8 characters"
    When I try to register with an email that is already registered
    Then I should see an error message "Email already registered"

  Scenario: Application form validation requires company selection
    Given I am logged in as a USER
    When I visit the new application page
    And I click Save without selecting a company
    Then I should see an error message "Company is required"

  Scenario: Loading and retry states are shown on slow/failing network
    Given I am logged in as a USER
    When I throttle the network and reload the dashboard
    Then I should see "Loading applications..."
    When I gointo offline and try to filter the applications
    Then I should see a "Failed to load applications" message
    And I should see a Retry button
    When I restore network and click Retry
    Then the dashboard should recover to the empty or list state

  @Responsive
  Scenario: No horizontal overflow on mobile viewport across key pages
    Given I am logged in
    When I view the app at 375px width
    Then the page should not horizontally scroll on login, dashboard, admin and form pages
