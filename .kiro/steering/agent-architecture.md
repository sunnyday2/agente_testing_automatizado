---
inclusion: fileMatch
fileMatchPattern: "**/src/agent/**,**/src/rag/**,**/src/crawler/**"
---

# Agent Architecture: LangGraph & RAG Patterns

## RAG System Design

### Document Loading
- Use `UnstructuredMarkdownLoader` for .md files, `JSONLoader` for .json
- Preserve document structure: title, epic, feature metadata must be extractable
- Reject documents that don't match expected schema (log warning, skip)

### Chunking Strategy
```python
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    separators=["\n## ", "\n### ", "\n\n", "\n", " "],
)
```
- Separators ordered to preserve user story boundaries
- Each chunk retains parent document metadata (filename, epic, feature)

### Embedding Provider Pattern
```python
class EmbeddingProvider:
    """Abstraction over embedding backends with automatic fallback."""

    def get_embeddings(self) -> Embeddings:
        try:
            return OllamaEmbeddings(model="qwen2.5:7b")
        except ConnectionError:
            return GoogleGenerativeAIEmbeddings(model="models/embedding-001")
```

### Vector Store Conventions
- Collection name format: `user_stories_v{version}`
- Always use persistent client mode: `chromadb.PersistentClient(path="./data/chroma")`
- Include metadata filters in queries when epic/feature is known
- Default similarity search: `top_k=3`, distance threshold `< 0.8`

## LangGraph Agent Design

### State Machine Principles
- State is the ONLY way to pass data between nodes
- Every node receives full state, returns partial state update
- Use `Annotated[list, operator.add]` for accumulating results
- Never mutate state directly — always return new values

### Node Implementation Pattern
```python
def generate_tests_node(state: AgentState) -> dict:
    """Generate test scenarios from retrieved documents.

    Args:
        state: Current agent state with retrieved_docs populated.

    Returns:
        Partial state update with test_scenarios field.
    """
    docs = state["retrieved_docs"]
    prompt = build_test_generation_prompt(docs)
    response = llm.invoke(prompt)
    scenarios = parse_scenarios(response)
    return {"test_scenarios": scenarios}
```

### Conditional Edge Pattern
```python
def route_after_generation(state: AgentState) -> str:
    """Determine next step based on generation results."""
    if not state.get("test_scenarios"):
        return "retry_generation"
    if state.get("crawl_results"):
        return "generate_pom_classes"
    return "publish_to_plane"
```

### LLM Provider Abstraction
- Never call LLM directly in nodes — always go through `llm_provider.py`
- Provider handles:
  - Model selection (local vs cloud)
  - Retry with exponential backoff (max 3 attempts)
  - Fallback switching on connection failure
  - Response parsing and validation
- Use structured output (Pydantic models) for all LLM responses:
  ```python
  class TestScenario(BaseModel):
      title: str
      description: str
      steps: list[str]
      expected_result: str
      priority: Literal["P1", "P2", "P3"]
      tags: list[str]
  ```

### Prompt Engineering Standards
- Store prompts in `src/agent/prompts/` as Python modules
- Use f-strings or `.format()` for variable injection (not Jinja2)
- Every prompt must include:
  - Clear role/persona definition
  - Output format specification (JSON schema)
  - 1-2 few-shot examples
  - Constraints and boundaries
- Keep prompts under 2000 tokens to leave room for context

## Site Crawler Design

### Crawl Engine Pattern
- BFS (Breadth-First Search) traversal with visited URL tracking
- Normalize URLs before deduplication (strip fragments, trailing slashes)
- Respect `robots.txt` when possible
- Use Playwright's `page.goto()` with `wait_until="networkidle"`

### Element Extraction
- Catalog all interactive elements per page:
  - Buttons (including submit buttons in forms)
  - Links (internal navigation)
  - Form inputs (text, email, password, select, checkbox)
  - Navigation menus
- Store elements with their selector, type, text content, and visibility state

### Site Map Structure
```python
@dataclass
class PageNode:
    url: str
    title: str
    elements: list[PageElement]
    screenshot_path: Optional[str]
    links_to: list[str]  # outgoing URLs
    depth: int

@dataclass
class SiteMap:
    root_url: str
    pages: list[PageNode]
    crawl_config: CrawlConfig
    timestamp: datetime
```

### Test Generation from Crawl
- LLM receives site map summary (not raw DOM)
- Generate tests grouped by user flow (not by page)
- Priority: login flows > navigation > forms > static content
- Each generated test file targets one flow with setup/teardown
- Generated POM classes match the patterns in `tests/e2e/pages/`

## Error Recovery

- RAG queries that return empty results: log warning, proceed with full-text LLM query
- LLM responses that fail schema validation: retry with stricter prompt, max 2 retries
- Crawler pages that timeout: mark as "unreachable", continue to next page
- Agent state corruption: checkpoint before each node, restore on failure
