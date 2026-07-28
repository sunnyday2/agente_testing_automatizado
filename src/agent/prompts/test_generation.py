"""Prompt templates for test scenario generation.

Contains the system prompt, user prompt template, and few-shot examples
used by the generate node to produce TestScenario objects from user stories.
"""

SYSTEM_PROMPT = """You are an expert QA automation engineer specializing in end-to-end \
test design. Your task is to generate comprehensive test scenarios from user stories.

Rules:
1. Each scenario must be atomic — testing exactly one behavior.
2. Include both positive (happy path) and negative (error) scenarios.
3. Steps must be concrete and automatable with Playwright.
4. Use CSS selector hints where the UI element is identifiable from the story.
5. Assign priorities: P1 = blocks release, P2 = important regression, P3 = edge case.
6. Tag each scenario with relevant categories for filtering.
7. Respond ONLY with valid JSON matching the provided schema."""

USER_PROMPT_TEMPLATE = """Generate test scenarios for the following user story.

## User Story
{user_story}

## Additional Context from Related Stories
{rag_context}

## Requirements
- Generate between 3 and 8 test scenarios covering:
  - Happy path (at least 1 scenario, P1)
  - Validation/error handling (at least 1 scenario, P1 or P2)
  - Edge cases and boundary conditions (P2 or P3)
- Each scenario must include concrete, automatable steps.
- Include preconditions needed before the test can run.
- Add selector hints where UI elements are described in the story.

Respond with a JSON object matching the TestGenerationResult schema."""

# Few-shot example for guiding the LLM output format
FEW_SHOT_EXAMPLE = """\
## Example Input
User Story: "As a registered user, I want to log in with my email and password, \
so that I can access my dashboard."
Acceptance Criteria:
- Valid credentials redirect to dashboard
- Invalid password shows error message
- Empty email disables login button

## Example Output
```json
{
  "scenarios": [
    {
      "title": "Successful login with valid credentials",
      "description": "Verify that a user with valid email and password is redirected to the dashboard after login.",
      "priority": "P1",
      "test_type": "smoke",
      "preconditions": [
        "User account exists with email 'testuser@example.com' and password 'SecurePass123!'",
        "User is on the login page"
      ],
      "steps": [
        {
          "action": "Enter email 'testuser@example.com' into the email field",
          "expected_result": "Email field displays the entered value",
          "selector_hint": "input[type='email']"
        },
        {
          "action": "Enter password 'SecurePass123!' into the password field",
          "expected_result": "Password field shows masked characters",
          "selector_hint": "input[type='password']"
        },
        {
          "action": "Click the 'Log In' button",
          "expected_result": "User is redirected to /dashboard",
          "selector_hint": "button[type='submit']"
        }
      ],
      "tags": ["login", "auth", "happy-path", "smoke"],
      "story_id": "US-001"
    },
    {
      "title": "Login fails with incorrect password",
      "description": "Verify that entering a wrong password shows an error message and does not redirect.",
      "priority": "P1",
      "test_type": "regression",
      "preconditions": [
        "User account exists with email 'testuser@example.com'",
        "User is on the login page"
      ],
      "steps": [
        {
          "action": "Enter email 'testuser@example.com' into the email field",
          "expected_result": "Email field displays the entered value",
          "selector_hint": "input[type='email']"
        },
        {
          "action": "Enter incorrect password 'WrongPass!' into the password field",
          "expected_result": "Password field shows masked characters",
          "selector_hint": "input[type='password']"
        },
        {
          "action": "Click the 'Log In' button",
          "expected_result": "Error message 'Invalid credentials' is displayed",
          "selector_hint": ".error-message"
        }
      ],
      "tags": ["login", "auth", "negative", "validation"],
      "story_id": "US-001"
    },
    {
      "title": "Login button disabled when email is empty",
      "description": "Verify that the login button remains disabled until the email field has content.",
      "priority": "P2",
      "test_type": "regression",
      "preconditions": [
        "User is on the login page",
        "Email field is empty"
      ],
      "steps": [
        {
          "action": "Observe the 'Log In' button state without entering any data",
          "expected_result": "Log In button is disabled (not clickable)",
          "selector_hint": "button[type='submit']"
        },
        {
          "action": "Enter email 'user@example.com' into the email field",
          "expected_result": "Log In button becomes enabled",
          "selector_hint": "input[type='email']"
        }
      ],
      "tags": ["login", "auth", "validation", "ui-state"],
      "story_id": "US-001"
    }
  ],
  "source_story_summary": "User login with email and password for dashboard access",
  "coverage_notes": "Covers happy path login, invalid credentials, and empty field validation. Does not cover account lockout (separate story)."
}
```"""


def build_test_generation_prompt(
    user_story: str,
    rag_context: str = "",
    story_id: str = "",
) -> tuple[str, str]:
    """Build the complete prompt pair for test generation.

    Args:
        user_story: The full text of the user story.
        rag_context: Additional context from similar stories (RAG retrieval).
        story_id: The source story identifier.

    Returns:
        Tuple of (system_prompt, user_prompt) ready for the LLM.
    """
    system = f"{SYSTEM_PROMPT}\n\n{FEW_SHOT_EXAMPLE}"

    context_section = rag_context if rag_context else "No additional context available."

    user = USER_PROMPT_TEMPLATE.format(
        user_story=user_story,
        rag_context=context_section,
    )

    if story_id:
        user += f"\n\nSource story ID: {story_id}"

    return system, user
