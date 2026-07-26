"""RAG (Retrieval-Augmented Generation) package.

Handles document ingestion, text splitting, embedding,
vector storage, and semantic retrieval of user stories.
"""

from src.rag.embeddings import get_embedding_function, get_embedding_with_fallback
from src.rag.loader import StoryLoader
from src.rag.retriever import RetrievalResult, StoryRetriever
from src.rag.splitter import StorySplitter
from src.rag.vectorstore import VectorStoreManager

__all__ = [
    "StoryLoader",
    "StorySplitter",
    "VectorStoreManager",
    "StoryRetriever",
    "RetrievalResult",
    "get_embedding_function",
    "get_embedding_with_fallback",
]
