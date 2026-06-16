# DocMind

Ask anything about your documents — get answers with citations.

![Demo](assets/demo.gif)

## Features
- **Multi-format Support**: Ingest and query PDF, TXT, DOCX files, and raw Web URLs.
- **Robust Semantic Chunking**: Splitting files using SentenceSplitter, adjusting parameters like chunk size and overlaps.
- **State-of-the-Art Models**: OpenAI embedding (`text-embedding-3-small`) combined with Anthropic Claude 3.5 Sonnet (`claude-3-5-sonnet-20241022`) for context synthesis.
- **Deterministic Cite Citations**: Exact citation mappings displaying text snippets, source document tags, and vector similarity match scores.
- **Strict Relevance Fallback**: Discards chunks below `SIMILARITY_CUTOFF` and warns when no context is relevant.
- **Premium User Interface**: Dark mode dashboard, sleek layouts, interactive sidebar indexing, and a chat canvas.

## Architecture

```
                       +-------------------+
                       |    Documents /    |
                       |  URLs Uploaded    |
                       +---------+---------+
                                 |
                                 v
                       +---------+---------+
                       | Sentence Splitter |
                       +---------+---------+
                                 | (Chunks)
                                 v
                       +---------+---------+
                       | OpenAI Embeddings |
                       +---------+---------+
                                 | (Vectors)
                                 v
                       +---------+---------+
                       |   Persistent DB   |
                       |    (Chroma)       |
                       +---------+---------+
                                 ^
                                 |
                       +---------+---------+
                       |  Retrieval & Top K| <----+ User Query
                       +---------+---------+
                                 |
                       +---------+---------+
                       | Similarity Cutoff |
                       +---------+---------+
                                 | (Filtered Chunks)
                                 v
                       +---------+---------+
                       | Anthropic LLM     |
                       | (Claude-3.5)      |
                       +---------+---------+
                                 |
                                 v
                       +---------+---------+
                       | Coherent Answer   |
                       |  with Citations   |
                       +-------------------+
```

## Quickstart

Get started with the following five commands:

```bash
git clone https://github.com/username/docmind.git && cd docmind
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
streamlit run app.py
```

## Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `OPENAI_API_KEY` | OpenAI API Secret Key for Embeddings | N/A | Yes |
| `ANTHROPIC_API_KEY` | Anthropic API Secret Key for Claude | N/A | Yes |
| `CHROMA_PERSIST_DIR` | Local persistence directory for Chroma DB | `./chroma_db` | No |
| `COLLECTION_NAME` | Chroma Collection identifier | `docmind` | No |
| `CHUNK_SIZE` | Size limit of document sentence splitting chunks | `512` | No |
| `CHUNK_OVERLAP` | Character size overlaps for sentence chunks | `64` | No |
| `TOP_K` | Retrospective candidate numbers matching query | `3` | No |
| `SIMILARITY_CUTOFF`| Score limit threshold matching query values | `0.7` | No |

## Usage

### Ingesting Documents (CLI)
You can ingest files, folders, or web URLs into the local vector DB:
```bash
python ingest.py --source ./docs
# Or index a web page:
python ingest.py --source https://example.com/ai-overview
```

### Querying the Engine Programmatically
```python
from query import answer

result = answer("What is Retrieval-Augmented Generation?")
print("Answer:", result["answer"])
for source in result["sources"]:
    print(f"- Source: {source['source']} (Score: {source['score']:.4f})")
```

## Project Structure
```
docmind/
├── app.py                  # Streamlit UI entry point
├── ingest.py               # CLI script to index documents
├── query.py                # Query engine logic (importable module)
├── config.py               # Centralised config from env vars
├── requirements.txt        # Pinned dependencies
├── .env.example            # Env var template
├── .gitignore              # Python + env + chroma ignores
├── README.md               # Full project README
├── JOURNAL.md              # Decision log and progress tracker
├── docs/                   # Sample documents folder
│   └── sample.txt          # A 200-word sample document about AI
├── chroma_db/              # Created at runtime by Chroma (gitignored)
└── tests/
    ├── test_ingest.py      # Unit tests for ingestion
    └── test_query.py       # Unit tests for query engine
```

## What I Learned
* → Leveraging LlamaIndex orchestrations makes integrating custom splitters and custom vector stores like Chroma seamless and modular.
* → Designing custom parser scrapers for URL sources using BeautifulSoup provides reliable textual input, avoiding bulky scraper dependencies.
* → Custom similarity cutoff rules at the retriever query boundary are crucial to prevent the LLM from synthesizing answers based on noisy, irrelevant data.

## Roadmap
- [ ] Support hybrid vector-keyword searches by integrating BM25 indexing.
- [ ] Add chunk hierarchy configurations (e.g. parent-child retrievals).
- [ ] Implement query expansion/reformulation to refine multi-turn user dialogues.
- [ ] Add support for password-protecting private Streamlit sessions.
- [ ] Integrate local, open-source embeddings (e.g., HuggingFace transformers) to allow offline capabilities.

## License
MIT License. Feel free to use and adapt this project for your own portfolio.
