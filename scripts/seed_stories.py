#!/usr/bin/env python3
"""Seed sample user stories into ChromaDB.

Loads all user story documents from data/stories/, chunks them,
generates embeddings, and stores them in ChromaDB for RAG retrieval.

Usage:
    python scripts/seed_stories.py
    python scripts/seed_stories.py --stories-dir ./data/stories
    python scripts/seed_stories.py --reset  # Clear collection first
"""

import argparse
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))


def main() -> None:
    """Load and embed user stories into ChromaDB."""
    parser = argparse.ArgumentParser(
        description="Seed user stories into ChromaDB vector store"
    )
    parser.add_argument(
        "--stories-dir",
        type=str,
        default=str(project_root / "data" / "stories"),
        help="Directory containing user story files",
    )
    parser.add_argument(
        "--reset",
        action="store_true",
        help="Delete existing collection before seeding",
    )
    parser.add_argument(
        "--collection",
        type=str,
        default="user_stories_v1",
        help="ChromaDB collection name",
    )
    args = parser.parse_args()

    print(f"🔍 Loading stories from: {args.stories_dir}")
    print(f"📦 Target collection: {args.collection}")
    print()

    # Import after path setup
    from src.common.logging import setup_logging
    from src.config.settings import get_settings
    from src.rag.loader import StoryLoader
    from src.rag.splitter import StorySplitter
    from src.rag.vectorstore import VectorStoreManager

    setup_logging(log_level="INFO", log_format="console")
    settings = get_settings()

    # Step 1: Load documents
    print("📄 Step 1: Loading documents...")
    loader = StoryLoader(stories_dir=args.stories_dir)
    documents = loader.load_all()

    if not documents:
        print("❌ No documents found. Check the stories directory.")
        sys.exit(1)

    print(f"   Found {len(documents)} document(s)")
    for doc in documents:
        source = doc.metadata.get("source", "unknown")
        story_id = doc.metadata.get("story_id", "N/A")
        print(f"   - {Path(source).name} (ID: {story_id})")

    # Step 2: Split into chunks
    print("\n✂️  Step 2: Splitting into chunks...")
    splitter = StorySplitter(
        chunk_size=settings.rag.chunk_size,
        chunk_overlap=settings.rag.chunk_overlap,
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunk(s)")

    # Step 3: Initialize vector store
    print("\n🗄️  Step 3: Initializing vector store...")
    try:
        vectorstore = VectorStoreManager(collection_name=args.collection)
    except Exception as e:
        print(f"❌ Failed to initialize vector store: {e}")
        print("   Make sure your embedding provider is running (Ollama or Gemini API key set)")
        sys.exit(1)

    # Reset collection if requested
    if args.reset:
        print("   🗑️  Resetting collection...")
        vectorstore.delete_collection()
        vectorstore = VectorStoreManager(collection_name=args.collection)
        print("   Collection cleared.")

    # Step 4: Add documents to vector store
    print("\n📥 Step 4: Embedding and storing chunks...")
    try:
        ids = vectorstore.add_documents(chunks)
        print(f"   ✅ Successfully stored {len(ids)} chunk(s)")
    except Exception as e:
        print(f"❌ Failed to store documents: {e}")
        sys.exit(1)

    # Step 5: Verify
    print("\n🔎 Step 5: Verifying storage...")
    stats = vectorstore.get_collection_stats()
    print(f"   Collection: {stats['name']}")
    print(f"   Total documents: {stats['count']}")

    # Test retrieval
    print("\n🧪 Step 6: Testing retrieval...")
    test_query = "login authentication test"
    from src.rag.retriever import StoryRetriever

    retriever = StoryRetriever(vectorstore_manager=vectorstore)
    result = retriever.retrieve(query=test_query, top_k=2)
    print(f"   Query: '{test_query}'")
    print(f"   Results: {result.count} document(s)")
    for i, doc in enumerate(result.documents):
        print(f"   [{i+1}] Score: {result.scores[i]:.4f} - {doc.page_content[:80]}...")

    print("\n✅ Seeding complete!")
    print(f"   Collection '{args.collection}' has {stats['count']} chunks ready for retrieval.")


if __name__ == "__main__":
    main()
