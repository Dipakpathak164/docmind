# Project Journal & Progress Log

**Start Date**: June 16, 2026

## Why I Built This
DocMind was developed to solve the "hallucination problem" associated with deploying Large Language Models (LLMs) on private, proprietary, or highly dynamic document databases. While tools like ChatGPT offer general conversational utility, they lack awareness of private corporate records or recently compiled research. By building a production-grade RAG pipeline using LlamaIndex, Chroma, and Streamlit, this portfolio project showcases a modular, secure, and explainable AI system capable of answering specific questions and anchoring those answers in verifiable, similarity-scored source documents.

---

## Decision Log

| Date | Decision | Alternatives Considered | Rationale |
|------|----------|-------------------------|-----------|
| 2026-06-16 | Chroma Vector Store | Pinecone, Qdrant | Chroma operates entirely locally and persistently without requiring external cloud accounts or subscription endpoints, making it perfect for private deployment, rapid integration, and seamless local integration in developer projects. |
| 2026-06-16 | claude-3-5-sonnet LLM | GPT-4o, GPT-3.5-Turbo | Claude 3.5 Sonnet exhibits superior context alignment, higher accuracy in following document synthesis constraints, and is less prone to answering questions outside the given context boundaries. |
| 2026-06-16 | Streamlit UI | Gradio, custom React frontend | Streamlit enables rich interactive component bindings (file uploads, expandable citation lists, chat states) directly from a Python script, avoiding the build overhead of standard frontend architectures. |

---

## Blockers Log

| Date | Blocker Description | Impact | Resolution |
|------|---------------------|--------|------------|
|      |                     |        |            |

---

## Week 1 Progress

- [x] Initial folder structure bootstrapping and file configuration
- [x] Configure dotenv loaders and validations in `config.py`
- [x] Write ingestion module `ingest.py` supporting URL retrieval and file parsing
- [x] Develop search core, query routing, and LLM text generation in `query.py`
- [x] Create interactive Web client frontend with citation components in `app.py`
- [x] Write pytest unit tests with mock behaviors in `tests/test_ingest.py` and `tests/test_query.py`
- [x] Populate initial RAG introduction documentation in `docs/sample.txt`
- [x] Setup git tracking and finalize initial commit
