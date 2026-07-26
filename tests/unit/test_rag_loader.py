"""Unit tests for RAG document loader."""

import json
import tempfile
from pathlib import Path

import pytest

from src.common.exceptions import DocumentLoadError
from src.rag.loader import StoryLoader


@pytest.fixture
def stories_dir(tmp_path: Path) -> Path:
    """Create a temp directory with sample story files."""
    return tmp_path


@pytest.fixture
def markdown_story(stories_dir: Path) -> Path:
    """Create a sample markdown story file."""
    content = """\
---
epic: User Authentication
feature: Login Flow
target_role: QA Engineer
priority: P1
story_id: US-001
---

# User Login

**As a** registered user
**I want** to log in with my email and password
**So that** I can access my dashboard

## Acceptance Criteria

- Given valid credentials, login succeeds
- Given invalid password, error message is shown
"""
    file_path = stories_dir / "test_story.md"
    file_path.write_text(content)
    return file_path


@pytest.fixture
def json_story(stories_dir: Path) -> Path:
    """Create a sample JSON story file."""
    data = [
        {
            "story_id": "US-002",
            "epic": "Dashboard",
            "feature": "Widgets",
            "target_role": "Chef",
            "priority": "P2",
            "title": "Widget Customization",
            "as_a": "product manager",
            "i_want": "to rearrange widgets",
            "so_that": "I can prioritize relevant info",
            "acceptance_criteria": [
                "Given I drag a widget, it snaps to grid",
                "Given I refresh, layout persists",
            ],
        }
    ]
    file_path = stories_dir / "test_story.json"
    file_path.write_text(json.dumps(data))
    return file_path


class TestStoryLoader:
    """Tests for StoryLoader class."""

    @pytest.mark.unit
    def test_load_markdown_extracts_metadata(self, stories_dir: Path, markdown_story: Path):
        """Verify markdown frontmatter metadata is extracted."""
        loader = StoryLoader(stories_dir=stories_dir)
        docs = loader.load_all()

        assert len(docs) >= 1
        md_doc = next(d for d in docs if d.metadata.get("file_type") == "markdown")
        assert md_doc.metadata["epic"] == "User Authentication"
        assert md_doc.metadata["feature"] == "Login Flow"
        assert md_doc.metadata["target_role"] == "QA Engineer"
        assert md_doc.metadata["story_id"] == "US-001"

    @pytest.mark.unit
    def test_load_markdown_extracts_body(self, stories_dir: Path, markdown_story: Path):
        """Verify markdown body content is preserved without frontmatter."""
        loader = StoryLoader(stories_dir=stories_dir)
        docs = loader.load_all()

        md_doc = next(d for d in docs if d.metadata.get("file_type") == "markdown")
        assert "# User Login" in md_doc.page_content
        assert "As a" in md_doc.page_content
        assert "---" not in md_doc.page_content  # frontmatter removed

    @pytest.mark.unit
    def test_load_json_extracts_metadata(self, stories_dir: Path, json_story: Path):
        """Verify JSON story metadata is extracted."""
        loader = StoryLoader(stories_dir=stories_dir)
        docs = loader.load_all()

        json_doc = next(d for d in docs if d.metadata.get("file_type") == "json")
        assert json_doc.metadata["epic"] == "Dashboard"
        assert json_doc.metadata["feature"] == "Widgets"
        assert json_doc.metadata["story_id"] == "US-002"

    @pytest.mark.unit
    def test_load_json_builds_story_text(self, stories_dir: Path, json_story: Path):
        """Verify JSON fields are assembled into readable text."""
        loader = StoryLoader(stories_dir=stories_dir)
        docs = loader.load_all()

        json_doc = next(d for d in docs if d.metadata.get("file_type") == "json")
        assert "Widget Customization" in json_doc.page_content
        assert "product manager" in json_doc.page_content
        assert "rearrange widgets" in json_doc.page_content
        assert "Acceptance Criteria" in json_doc.page_content

    @pytest.mark.unit
    def test_load_all_from_mixed_directory(
        self, stories_dir: Path, markdown_story: Path, json_story: Path
    ):
        """Verify loading both MD and JSON files from the same directory."""
        loader = StoryLoader(stories_dir=stories_dir)
        docs = loader.load_all()

        assert len(docs) >= 2
        file_types = {d.metadata["file_type"] for d in docs}
        assert "markdown" in file_types
        assert "json" in file_types

    @pytest.mark.unit
    def test_load_empty_directory(self, tmp_path: Path):
        """Verify loading from empty directory returns no documents."""
        loader = StoryLoader(stories_dir=tmp_path)
        docs = loader.load_all()
        assert docs == []

    @pytest.mark.unit
    def test_load_nonexistent_directory(self, tmp_path: Path):
        """Verify loading from missing directory returns empty list."""
        loader = StoryLoader(stories_dir=tmp_path / "nonexistent")
        docs = loader.load_all()
        assert docs == []

    @pytest.mark.unit
    def test_load_file_unsupported_format(self, tmp_path: Path):
        """Verify unsupported file extension raises DocumentLoadError."""
        file_path = tmp_path / "story.txt"
        file_path.write_text("some text")

        loader = StoryLoader(stories_dir=tmp_path)
        with pytest.raises(DocumentLoadError):
            loader.load_file(file_path)

    @pytest.mark.unit
    def test_load_file_single_markdown(self, markdown_story: Path):
        """Verify loading a single markdown file directly."""
        loader = StoryLoader(stories_dir=markdown_story.parent)
        docs = loader.load_file(markdown_story)

        assert len(docs) == 1
        assert docs[0].metadata["story_id"] == "US-001"
