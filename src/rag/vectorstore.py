"""ChromaDB vector store initialization and management.

Provides a persistent ChromaDB client for storing and querying user story
embeddings. Supports collection versioning to allow schema evolution
without data loss.

Usage:
    from src.rag.vectorstore import VectorStoreManager

    manager = VectorStoreManager()
    manager.add_documents(documents)
    results = manager.similarity_search("login test", k=3)
"""

from pathlib import Path

import chromadb
from chromadb.config import Settings as ChromaSettings
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from src.common.exceptions import EmbeddingError, RetrievalError
from src.common.logging import get_logger
from src.config.settings import get_settings
from src.rag.embeddings import get_embedding_with_fallback

logger = get_logger(__name__)


class VectorStoreManager:
    """Manages ChromaDB vector store lifecycle and operations.

    Handles persistent storage initialization, collection versioning,
    document indexing, and similarity search queries.
    """

    def __init__(
        self,
        persist_directory: str | None = None,
        collection_name: str | None = None,
        embedding_function: Embeddings | None = None,
    ) -> None:
        """Initialize the vector store manager.

        Args:
            persist_directory: Path to ChromaDB persistent storage.
                Defaults to settings value.
            collection_name: Name of the vector collection.
                Defaults to settings value (user_stories_v1).
            embedding_function: Custom embedding function.
                Defaults to auto-selected provider with fallback.
        """
        settings = get_settings()
        self._persist_directory = persist_directory or settings.chromadb.persist_directory
        self._collection_name = collection_name or settings.chromadb.collection_name
        self._distance_function = settings.chromadb.distance_function

        # Ensure persist directory exists
        Path(self._persist_directory).mkdir(parents=True, exist_ok=True)

        # Initialize embedding function
        self._embedding_function = embedding_function or self._init_embeddings()

        # Initialize ChromaDB client and LangChain wrapper
        self._client = self._init_client()
        self._vectorstore = self._init_vectorstore()

        logger.info(
            "vectorstore_initialized",
            persist_directory=self._persist_directory,
            collection_name=self._collection_name,
        )

    def _init_embeddings(self) -> Embeddings:
        """Initialize embedding function with fallback support."""
        try:
            return get_embedding_with_fallback()
        except EmbeddingError:
            logger.error("embedding_initialization_failed")
            raise

    def _init_client(self) -> chromadb.ClientAPI:
        """Initialize the persistent ChromaDB client."""
        return chromadb.PersistentClient(
            path=self._persist_directory,
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            ),
        )

    def _init_vectorstore(self) -> Chroma:
        """Initialize the LangChain Chroma wrapper."""
        return Chroma(
            client=self._client,
            collection_name=self._collection_name,
            embedding_function=self._embedding_function,
            collection_metadata={"hnsw:space": self._distance_function},
        )

    @property
    def collection_name(self) -> str:
        """Return the current collection name."""
        return self._collection_name

    def add_documents(self, documents: list[Document]) -> list[str]:
        """Add documents to the vector store.

        Args:
            documents: List of LangChain Document objects to embed and store.

        Returns:
            List of document IDs assigned by ChromaDB.
        """
        if not documents:
            logger.warning("add_documents_called_with_empty_list")
            return []

        logger.info("adding_documents", count=len(documents))
        ids = self._vectorstore.add_documents(documents)
        logger.info("documents_added", count=len(ids))
        return ids

    def similarity_search(
        self,
        query: str,
        k: int = 3,
        filter_metadata: dict | None = None,
    ) -> list[Document]:
        """Search for documents similar to the query.

        Args:
            query: The search query text.
            k: Number of results to return.
            filter_metadata: Optional metadata filter for ChromaDB where clause.

        Returns:
            List of matching Document objects ordered by similarity.

        Raises:
            RetrievalError: If the search operation fails.
        """
        try:
            kwargs: dict = {"k": k}
            if filter_metadata:
                kwargs["filter"] = filter_metadata

            results = self._vectorstore.similarity_search(query, **kwargs)
            logger.info(
                "similarity_search_completed",
                query=query[:80],
                results_count=len(results),
            )
            return results
        except Exception as e:
            raise RetrievalError(query=query, reason=str(e)) from e

    def similarity_search_with_score(
        self,
        query: str,
        k: int = 3,
        filter_metadata: dict | None = None,
    ) -> list[tuple[Document, float]]:
        """Search with relevance scores for threshold filtering.

        Args:
            query: The search query text.
            k: Number of results to return.
            filter_metadata: Optional metadata filter.

        Returns:
            List of (Document, score) tuples. Lower score = more similar
            for cosine distance.

        Raises:
            RetrievalError: If the search operation fails.
        """
        try:
            kwargs: dict = {"k": k}
            if filter_metadata:
                kwargs["filter"] = filter_metadata

            results = self._vectorstore.similarity_search_with_score(query, **kwargs)
            logger.info(
                "similarity_search_with_score_completed",
                query=query[:80],
                results_count=len(results),
            )
            return results
        except Exception as e:
            raise RetrievalError(query=query, reason=str(e)) from e

    def delete_collection(self) -> None:
        """Delete the current collection and all its data.

        Use with caution — this is irreversible.
        """
        logger.warning("deleting_collection", collection_name=self._collection_name)
        self._client.delete_collection(self._collection_name)
        self._vectorstore = self._init_vectorstore()

    def get_collection_stats(self) -> dict:
        """Get statistics about the current collection.

        Returns:
            Dictionary with collection metadata and document count.
        """
        collection = self._client.get_collection(self._collection_name)
        return {
            "name": self._collection_name,
            "count": collection.count(),
            "metadata": collection.metadata,
        }

    def list_collections(self) -> list[str]:
        """List all available collections in the ChromaDB instance.

        Returns:
            List of collection names.
        """
        collections = self._client.list_collections()
        return [c.name for c in collections]

    def switch_collection(self, collection_name: str) -> None:
        """Switch to a different collection (versioning support).

        Allows working with multiple collection versions (e.g.,
        user_stories_v1, user_stories_v2) for schema evolution.

        Args:
            collection_name: The target collection name to switch to.
        """
        logger.info(
            "switching_collection",
            from_collection=self._collection_name,
            to_collection=collection_name,
        )
        self._collection_name = collection_name
        self._vectorstore = self._init_vectorstore()
