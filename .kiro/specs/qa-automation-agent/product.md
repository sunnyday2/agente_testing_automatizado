# Product Requirements: QA Automation & Reporting Agent

## Problem Statement
QA teams spend significant time manually creating test cases from user stories, managing task boards, executing repetitive test suites, and compiling reports. This manual overhead reduces testing coverage and delays feedback loops between development and QA.

## Proposed Solution
An AI-powered QA Automation Agent that autonomously reads user stories, generates test scenarios using LLM intelligence, creates tasks in a project management board (Plane.so), executes Playwright-based automated tests when tasks move to "DOING", and produces Allure reports accessible to technical and non-technical stakeholders.

Additionally, the agent can receive a target URL, autonomously navigate and analyze the site, discover UI elements and user flows, and generate automated test scripts without requiring pre-existing user stories.

## User Personas

### QA Engineer
- Needs automated test generation from user stories
- Wants to focus on exploratory testing rather than writing repetitive E2E tests
- Requires detailed Allure reports with screenshots on failures
- Needs the ability to point the agent at a URL and get tests generated automatically

### Product Manager / Chef
- Writes user stories in Markdown/JSON format
- Wants visibility into test coverage without technical setup
- Needs accessible dashboards showing pass/fail status

### Developer
- Needs fast feedback on feature stability
- Wants to see which tests are related to their user stories
- Requires CSV exports of test metrics for sprint retrospectives

## Functional Requirements

### FR-1: User Story Ingestion
- The system SHALL accept user stories in Markdown (.md) and JSON (.json) formats
- The system SHALL parse stories preserving "As a / I want / So that" structure
- The system SHALL tag stories with metadata: epic, feature, target_role

### FR-2: Intelligent Test Scenario Generation
- The system SHALL generate test scenarios from ingested user stories using LLM
- The system SHALL assign priority levels (P1/P2/P3) to generated scenarios
- The system SHALL support local LLM (Ollama) with cloud fallback (Gemini API)

### FR-3: Task Board Integration
- The system SHALL create tasks in Plane.so with generated test scenarios
- The system SHALL organize tasks by priority in a QA Board (TODO/DOING/FINISHED/FAILED)
- The system SHALL listen to webhook events when tasks transition to "DOING"

### FR-4: Automated Test Execution
- The system SHALL execute Playwright tests when triggered by webhook events
- The system SHALL support headless browser execution (Chromium, Firefox)
- The system SHALL run tests by tag (smoke, regression)
- The system SHALL update task status to FINISHED or FAILED based on exit codes

### FR-5: Site Discovery & Autonomous Test Generation from URL
- The system SHALL accept a target site URL as input for automated analysis
- The system SHALL navigate the provided site using Playwright, crawling pages and discovering UI elements, forms, navigation paths, and interactive components
- The system SHALL use the LLM agent to analyze the discovered site structure and generate relevant test cases based on elements and user flows found
- The system SHALL identify critical user paths (login, navigation, forms, CRUD operations) autonomously by analyzing the DOM and interaction patterns
- The system SHALL produce Playwright test scripts following the Page Object Model pattern from the discovered site map
- The system SHALL store generated tests in the project test suite for subsequent execution and re-runs
- The system SHALL support configurable depth-limited crawling (max pages and max depth) to avoid infinite navigation loops
- The system SHALL extract and catalog all actionable elements (buttons, links, inputs, selects) per page for targeted test generation
- The system SHALL generate a site map report summarizing discovered pages, elements, and suggested test scenarios before execution

### FR-6: Reporting & Export
- The system SHALL generate Allure reports with feature/story annotations
- The system SHALL capture screenshots on test failures
- The system SHALL provide CSV export of test execution metrics via API endpoint
- The system SHALL serve Allure reports via a web-accessible dashboard

### FR-7: Automatic Git Commit After Successful Test
- The system SHALL automatically create a Git commit after each feature's tests pass successfully
- The commit message SHALL follow a structured format: `test(feature-name): PASSED - [timestamp] - [summary of tests run]`
- The system SHALL stage only test-related files (test results, generated test scripts, Allure artifacts) in the commit
- The system SHALL NOT commit if the test suite fails — only successful (FINISHED) test executions trigger a commit
- The system SHALL push the commit to the configured remote branch (configurable, default: current branch)
- The system SHALL tag the commit with test metadata (number of tests passed, execution time, feature name)
- The system SHALL support configurable commit behavior: commit-only, commit-and-push, or disabled
- The system SHALL log all commit operations with SHA, branch, and timestamp for audit trail

## Non-Functional Requirements

### NFR-1: Performance
- Webhook processing latency SHALL be < 2 seconds
- Test suite smoke runs SHALL complete within 5 minutes
- RAG similarity search SHALL respond within 500ms
- Site crawling SHALL complete within 3 minutes for sites up to 50 pages

### NFR-2: Reliability
- LLM provider failover SHALL be transparent (Ollama -> Gemini)
- Test execution SHALL retry once on transient browser failures
- System SHALL maintain state across container restarts (persistent ChromaDB)
- Site crawler SHALL handle navigation errors gracefully without aborting the full crawl

### NFR-3: Accessibility
- Allure dashboards SHALL be accessible via browser without local installation
- Plane.so board SHALL be accessible to non-technical users
- CSV exports SHALL be downloadable via simple GET request

### NFR-4: Scalability
- The system SHALL support concurrent test executions (up to 3 parallel)
- ChromaDB SHALL handle up to 10,000 user story chunks
- The system SHALL support multiple QA boards/projects
- Site discovery SHALL handle sites with up to 100 unique pages

## Success Metrics
- 85%+ RAG recall accuracy for user story retrieval
- 90%+ test execution success rate for smoke suites
- < 30 seconds from webhook receipt to test execution start
- Zero manual intervention required for standard test cycles
- Site discovery SHALL identify 90%+ of navigable pages within configured depth
- Generated tests from URL analysis SHALL achieve 80%+ valid execution rate
