---
epic: User Authentication
feature: Login Flow
target_role: QA Engineer
priority: P1
story_id: US-001
---

# User Login with Email and Password

**As a** registered user
**I want** to log in with my email and password
**So that** I can access my personalized dashboard

## Acceptance Criteria

- Given I am on the login page, I should see email and password fields
- Given I enter valid credentials and click "Log In", I should be redirected to the dashboard
- Given I enter an invalid email format, I should see a validation error message
- Given I enter a wrong password, I should see "Invalid credentials" error
- Given I leave the email field empty, the "Log In" button should be disabled
- Given I have 5 failed login attempts, my account should be temporarily locked for 15 minutes

## Notes

- Password field should mask input characters
- "Forgot password?" link should be visible below the password field
- Login form should be accessible via keyboard navigation (Tab order)
- Session token should expire after 24 hours of inactivity
