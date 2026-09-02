import os
import sys
from dotenv import load_dotenv

# Suppress ChromaDB anonymous telemetry warnings
os.environ["ANONYMOUS_TELEMETRY"] = "False"

# Load environment variables from .env
load_dotenv(override=True)



# Determine if we are running in a pytest environment
IS_TESTING = (
    os.getenv("TESTING", "false").lower() in ("true", "1", "yes")
    or "pytest" in sys.modules
    or "PYTEST_CURRENT_TEST" in os.environ
)

# Required API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")

# Treat placeholder values from the .env file as None
if OPENAI_API_KEY and ("your_openai_api_key" in OPENAI_API_KEY or OPENAI_API_KEY == "mock-openai-key" and not IS_TESTING):
    OPENAI_API_KEY = None
if ANTHROPIC_API_KEY and ("your_anthropic_api_key" in ANTHROPIC_API_KEY or ANTHROPIC_API_KEY == "mock-anthropic-key" and not IS_TESTING):
    ANTHROPIC_API_KEY = None
if GEMINI_API_KEY and ("your_gemini_api_key" in GEMINI_API_KEY or GEMINI_API_KEY == "mock-gemini-key" and not IS_TESTING):
    GEMINI_API_KEY = None

# Check required API keys unless we are executing unit tests
# We need at least one embedding key and one LLM key
has_embedding_key = bool(OPENAI_API_KEY or GEMINI_API_KEY)
has_llm_key = bool(ANTHROPIC_API_KEY or GEMINI_API_KEY)


if (not has_embedding_key or not has_llm_key) and not IS_TESTING:
    raise ValueError(
        "Insufficient API keys provided. To run DocMind, please configure either:\n"
        "1. GEMINI_API_KEY (for free embeddings & LLM)\n"
        "OR\n"
        "2. OPENAI_API_KEY (for embeddings) and GEMINI_API_KEY (for free LLM)\n"
        "OR\n"
        "3. OPENAI_API_KEY (for embeddings) and ANTHROPIC_API_KEY (for Claude LLM).\n"
        "Please edit your '.env' file."
    )

# Assign dummy keys in testing environment if not present
if IS_TESTING:
    OPENAI_API_KEY = OPENAI_API_KEY or "mock-openai-key"
    ANTHROPIC_API_KEY = ANTHROPIC_API_KEY or "mock-anthropic-key"
    GEMINI_API_KEY = GEMINI_API_KEY or "mock-gemini-key"



# Vector DB Configuration
CHROMA_PERSIST_DIR = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
COLLECTION_NAME = os.getenv("COLLECTION_NAME", "docmind")

# Chunking & Node Splitting Parameters
try:
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
except ValueError:
    CHUNK_SIZE = 512

try:
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "64"))
except ValueError:
    CHUNK_OVERLAP = 64

# Retrieval Configuration
try:
    TOP_K = int(os.getenv("TOP_K", "5"))
except ValueError:
    TOP_K = 5

try:
    SIMILARITY_CUTOFF = float(os.getenv("SIMILARITY_CUTOFF", "0.35"))
except ValueError:
    SIMILARITY_CUTOFF = 0.35


# Advanced Retrieval Features
HYBRID_SEARCH = os.getenv("HYBRID_SEARCH", "true").lower() in ("true", "1", "yes")

