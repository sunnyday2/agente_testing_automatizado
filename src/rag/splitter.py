"""Text splitting for user story documents.

Uses LangChain's RecursiveCharacterTextSplitter configured to preserve
semantic boundaries in user stories (sections, paragraphs, sentences).
Metadata is propagated from parent documents to all child chunks.

Usage:
    from src.rag.splitter import StorySplitter

    splitter = StorySplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(documents)
"""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.common.logging import get_logger

logger = get_logger(__name__)

# Separators ordered by priority — split at higher-level boundaries first
STORY_SEPARATORS = [
    "\n## ",       # Markdown H2 headers (Acceptance Criteria, Notes sections)
    "\n### ",      # Markdown H3 headers
    "\n# ",        # Markdown H1 headers (Story title)
    "\n\n",        # Double newline (paragraph breaks)
    "\n- ",        # List items (criteria, steps)
    "\n",          # Single newline
    ". ",          # Sentence boundary
    " ",           # Word boundary (last resort)
]


class StorySplitter:
    """Splits user story documents into semantic chunks for embedding.

    Preserves the structure of user stories by splitting at meaningful
    boundaries (headers, paragraphs, list items) rather than arbitrary
    character positions.

    Metadata from the source document is propagated to all child chunks,
    with additional chunk-level metadata (chunk_index, total_chunks).
    """

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        separators: list[str] | None = None,
    ) -> None:
        """Initialize the story splitter.

        Args:
            chunk_size: Maximum number of characters per chunk.
            chunk_overlap: Number of overlapping characters between chunks.
            separators: Custom separator list. Defaults to STORY_SEPARATORS.
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=separators or STORY_SEPARATORS,
            length_function=len,
            is_separator_regex=False,
        )

    def split_documents(self, documents: list[Document]) -> list[Document]:
        """Split a list of documents into smaller chunks.

        Each chunk inherits the metadata of its parent document and receives
        additional fields: chunk_index and total_chunks.

        Args:
            documents: List of Document objects to split.

        Returns:
            List of chunked Document objects with propagated metadata.
        """
        all_chunks: list[Document] = []

        for doc in documents:
            chunks = self._split_single(doc)
            all_chunks.extend(chunks)

        logger.info(
            "documents_split",
            input_documents=len(documents),
            output_chunks=len(all_chunks),
            avg_chunk_size=(
                sum(len(c.page_content) for c in all_chunks) // max(len(all_chunks), 1)
            ),
        )

        return all_chunks

    def _split_single(self, document: Document) -> list[Document]:
        """Split a single document and propagate metadata to chunks.

        Args:
            document: The source Document to split.

        Returns:
            List of chunk Documents with inherited + chunk-level metadata.
        """
        raw_chunks = self._splitter.split_text(document.page_content)

        chunks: list[Document] = []
        for idx, chunk_text in enumerate(raw_chunks):
            chunk_metadata = {
                **document.metadata,
                "chunk_index": idx,
                "total_chunks": len(raw_chunks),
            }
            chunks.append(Document(page_content=chunk_text, metadata=chunk_metadata))

        return chunks

    def split_text(self, text: str) -> list[str]:
        """Split raw text into chunks without metadata handling.

        Useful for splitting text that hasn't been wrapped in a Document yet.

        Args:
            text: Raw text content to split.

        Returns:
            List of text chunks.
        """
        return self._splitter.split_text(text)
