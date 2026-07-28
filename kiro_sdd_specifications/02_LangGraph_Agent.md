# Feature 2 Specification: LangGraph Orchestration & Decision Agent

## 1. System Overview
The LangGraph Agent acts as the intelligent decision maker. It receives retrieved user story contexts, constructs test scenarios, determines task priorities, and publishes work items directly to Plane.so.

## 2. Technical Stack
- **Framework:** `langgraph`, `langchain_core`
- **LLM Engine:** Local Ollama (`llama3.2` / `qwen2.5:7b`) with fallback to Google Gemini API (`gemini-2.5-flash`)
- **State Management:** TypedDict `AgentState`

## 3. Tasks Breakdown (Max 6 Tasks)

### [AGT-01] LangGraph State Definition
- Define schema: `user_story_text`, `retrieved_docs`, `test_scenarios`, `plane_task_id`, `execution_status`.

### [AGT-02] Decision Node Implementation
- Prompt engineering for test generation and priority assignment (P1/P2/P3).
- Structured output formatting using Pydantic models.

### [AGT-03] State Routing & Conditional Edges
- Implement conditional flow control: Story Ingestion ──> Test Extraction ──> Plane Task Creation.

### [AGT-04] LLM Provider Abstraction Layer
- Wrapper for zero-downtime transition between local Ollama and Cloud Gemini API.

### [AGT-05] Agent Integration Testing
- Execute mock user story runs to verify state machine reliability without external side-effects.