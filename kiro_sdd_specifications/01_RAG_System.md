# Feature 1 Specification: RAG System & User Story Loader

## 1. System Overview
The RAG System parses structured user story documents (Markdown/JSON) created by product managers and chefs, extracts semantic chunks, generates vector embeddings, and stores them in ChromaDB.

## 2. Technical Stack
- **Loader:** `langchain_community.document_loaders` (UnstructuredMarkdownLoader / JSONLoader)
- **Text Splitter:** `RecursiveCharacterTextSplitter` (chunk_size=500, chunk_overlap=50)
- **Embeddings:** `OllamaEmbeddings(model="qwen2.5:7b")` or `GoogleGenerativeAIEmbeddings`
- **Vector Database:** `chromadb` (Persistent Client Mode)

## 3. Tasks Breakdown (Max 6 Tasks)

### [RAG-01] Document Loader & Splitter Setup
- Implementation of standard file readers for Markdown and JSON user story formats.
- Configuration of semantic splitting rules preserving user story structures (As a / I want / So that).

### [RAG-02] Vector DB Initialization
- Setup persistent ChromaDB storage in `./data/chroma`.
- Configure default vector collection `user_stories_v1`.

### [RAG-03] Similarity Search Service
- Implement `StoryRetriever` service to search relevant context given a test query.
- Configure similarity threshold and `top_k=3` return limit.

### [RAG-04] Metadata Tagging Pipeline
- Extract and attach tags to document chunks: `epic`, `feature`, `target_role` (Chef / Dev).

### [RAG-05] RAG Verification Tests
- Build pytest suite testing vector recall precision against sample user story queries (>85% accuracy threshold).