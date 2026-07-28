# Kiro QA Automation & Reporting System - Specification Package

Welcome to the Software Design Document (SDD) package for project **Kiro**.
This directory contains modular, production-ready specifications for building the QA Automation & Reporting Engine.

## Tech Stack Overview
- **Core Language:** Python 3.11+
- **RAG & Agent:** LangChain + ChromaDB + LangGraph
- **LLM Support:** Ollama (Local) / Google Gemini API (Fallback)
- **API & Dispatcher:** FastAPI + Uvicorn
- **Task Management:** Plane.so (Docker)
- **Automation Engine:** Playwright Python (`pytest-playwright`)
- **Reporting Server:** Allure Framework Docker Server

## Architecture Overview
```
[User Stories (MD/JSON)] ──> [01_RAG_System.md]
                                   │
                                   ▼
                       [02_LangGraph_Agent.md] ──> Creates Tasks in Plane.so
                                                              │
                                                              ▼
                                                   [05_Infrastructure.md]
                                                              │ (Webhook: DOING)
                                                              ▼
                       [04_Playwright_Tests.md] <── [03_FastAPI_Engine.md]
                                   │                          │
                                   ▼                          ▼
                         [Allure Reports Server]      [CSV Export Endpoint]
```

## Directory Contents
1. `01_RAG_System.md` - Specification for User Stories Loading & ChromaDB Vector Store.
2. `02_LangGraph_Agent.md` - Specification for LLM Task Creation Agent & State Machine.
3. `03_FastAPI_Engine.md` - Specification for Webhook Handler, Playwright Dispatcher & CSV Exporter.
4. `04_Playwright_Tests.md` - Specification for Test Automation Suite & Allure Pytest integration.
5. `05_Infrastructure.md` - Specification for Docker Compose, Plane.so setup, and Allure Server.

---
*Maintained by: Kiro (QA Lead / Systems Architect)*