"""Document loaders for user stories in Markdown and JSON formats.

Loads user story files from the configured stories directory, extracts
metadata (epic, feature, target_role), and returns LangChain Document objects
ready for splitting and embedding.

Supported formats:
- Markdown (.md): Parses frontmatter-style metadata and story body
- JSON (.json): Expects structured objects with metadata fields

Usage:
    from src.rag.loader import StoryLoader

    loader = StoryLoader(stories_dir="./data/stories")
    documents = loader.load_all()
"""

import json
import re
from pathlib import Path

from langchain_core.documents import Document

from src.common.exceptions import DocumentLoadError
from src.common.logging import get_logger

logger = get_logger(__name__)

# Regex patterns for markdown metadata extraction
METADATA_PATTERN = re.compile(
    r"^---\s*\n(.*?)\n---\s*\n",
    re.DOTALL,
)
METADATA_FIELD_PATTERN = re.compile(r"^(\w+)\s*:\s*(.+)$", re.MULTILINE)

# Standard metadata keys we extract from stories
METADATA_KEYS = {"epic", "feature", "target_role", "priority", "story_id"}


class StoryLoader:
    """Loads user story documents from the filesystem.

    Supports Markdown and JSON file formats, extracting structured
    metadata from each story for use in RAG retrieval filtering.
    """

    def __init__(self, stories_dir: str | Path) -> None:
        """Initialize the story loader.

        Args:
            stories_dir: Path to the directory containing user story files.
        """
        self.stories_dir = Path(stories_dir)
        if not self.stories_dir.exists():
            logger.warning("stories_directory_not_found", path=str(self.stories_dir))

    def load_all(self) -> list[Document]:
        """Load all user story documents from the stories directory.

        Returns:
            List of LangChain Document objects with metadata.

        Raises:
            DocumentLoadError: If a file cannot be parsed.
        """
        documents: list[Document] = []

        if not self.stories_dir.exists():
            logger.warning("stories_directory_missing", path=str(self.stories_dir))
            return documents

        md_files = list(self.stories_dir.glob("**/*.md"))
        json_files = list(self.stories_dir.glob("**/*.json"))

        logger.info(
            "loading_stories",
            directory=str(self.stories_dir),
            markdown_files=len(md_files),
            json_files=len(json_files),
        )

        for file_path in md_files:
            try:
                docs = self._load_markdown(file_path)
                documents.extend(docs)
            except Exception as e:
                raise DocumentLoadError(
                    file_path=str(file_path), reason=str(e)
                ) from e

        for file_path in json_files:
            try:
                docs = self._load_json(file_path)
                documents.extend(docs)
            except Exception as e:
                raise DocumentLoadError(
                    file_path=str(file_path), reason=str(e)
                ) from e

        logger.info("stories_loaded", total_documents=len(documents))
        return documents

    def load_file(self, file_path: str | Path) -> list[Document]:
        """Load a single user story file.

        Args:
            file_path: Path to the file to load.

        Returns:
            List of Document objects from the file.

        Raises:
            DocumentLoadError: If the file format is unsupported or parsing fails.
        """
        path = Path(file_path)
        if path.suffix == ".md":
            return self._load_markdown(path)
        elif path.suffix == ".json":
            return self._load_json(path)
        else:
            raise DocumentLoadError(
                file_path=str(path),
                reason=f"Unsupported file format: {path.suffix}",
            )

    def _load_markdown(self, file_path: Path) -> list[Document]:
        """Parse a Markdown user story file.

        Expected format:
            ---
            epic: User Authentication
            feature: Login Flow
            target_role: QA Engineer
            priority: P1
            story_id: US-001
            ---

            # Story Title

            **As a** user
            **I want** to log in with my credentials
            **So that** I can access my dashboard

            ## Acceptance Criteria
            - Given valid credentials, login succeeds
            - Given invalid password, error message is shown
        """
        content = file_path.read_text(encoding="utf-8")

        # Extract frontmatter metadata
        metadata = self._extract_markdown_metadata(content)
        metadata["source"] = str(file_path)
        metadata["file_type"] = "markdown"

        # Remove frontmatter from content body
        body = METADATA_PATTERN.sub("", content).strip()

        if not body:
            logger.warning("empty_story_body", file=str(file_path))
            return []

        return [Document(page_content=body, metadata=metadata)]

    def _load_json(self, file_path: Path) -> list[Document]:
        """Parse a JSON user story file.

        Expected format (single story):
            {
                "story_id": "US-001",
                "epic": "User Authentication",
                "feature": "Login Flow",
                "target_role": "QA Engineer",
                "priority": "P1",
                "title": "User Login",
                "description": "As a user I want to...",
                "acceptance_criteria": ["Given...", "When...", "Then..."]
            }

        Or array of stories:
            [{ ... }, { ... }]
        """
        content = file_path.read_text(encoding="utf-8")
        data = json.loads(content)

        # Handle both single object and array formats
        stories = data if isinstance(data, list) else [data]

        documents: list[Document] = []
        for story in stories:
            metadata = self._extract_json_metadata(story)
            metadata["source"] = str(file_path)
            metadata["file_type"] = "json"

            # Build document content from story fields
            page_content = self._build_story_text(story)

            if page_content.strip():
                documents.append(Document(page_content=page_content, metadata=metadata))

        return documents

    def _extract_markdown_metadata(self, content: str) -> dict:
        """Extract metadata from markdown frontmatter block."""
        metadata: dict = {}

        match = METADATA_PATTERN.match(content)
        if not match:
            return metadata

        frontmatter = match.group(1)
        for field_match in METADATA_FIELD_PATTERN.finditer(frontmatter):
            key = field_match.group(1).strip().lower()
            value = field_match.group(2).strip()
            if key in METADATA_KEYS:
                metadata[key] = value

        return metadata

    def _extract_json_metadata(self, story: dict) -> dict:
        """Extract metadata fields from a JSON story object."""
        metadata: dict = {}
        for key in METADATA_KEYS:
            if key in story:
                metadata[key] = story[key]
        return metadata

    def _build_story_text(self, story: dict) -> str:
        """Build a readable text representation from a JSON story object."""
        parts: list[str] = []

        if "title" in story:
            parts.append(f"# {story['title']}")

        if "description" in story:
            parts.append(story["description"])

        # Build "As a / I want / So that" if individual fields exist
        if "as_a" in story:
            parts.append(f"**As a** {story['as_a']}")
        if "i_want" in story:
            parts.append(f"**I want** {story['i_want']}")
        if "so_that" in story:
            parts.append(f"**So that** {story['so_that']}")

        if "acceptance_criteria" in story:
            criteria = story["acceptance_criteria"]
            if isinstance(criteria, list):
                parts.append("\n## Acceptance Criteria")
                for criterion in criteria:
                    parts.append(f"- {criterion}")
            elif isinstance(criteria, str):
                parts.append(f"\n## Acceptance Criteria\n{criteria}")

        if "notes" in story:
            parts.append(f"\n## Notes\n{story['notes']}")

        return "\n\n".join(parts)
