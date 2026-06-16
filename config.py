import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

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

# Check required API keys unless we are executing unit tests
missing_keys = []
if not GEMINI_API_KEY:
    if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
        if not OPENAI_API_KEY:
            missing_keys.append("OPENAI_API_KEY")
        if not ANTHROPIC_API_KEY:
            missing_keys.append("ANTHROPIC_API_KEY")
        missing_keys.append("GEMINI_API_KEY")

if missing_keys and not IS_TESTING:
    raise ValueError(
        "Missing required environment variables. To run DocMind, you must set either:\n"
        "1. GEMINI_API_KEY (for the free Google Gemini tier)\n"
        "OR\n"
        "2. BOTH OPENAI_API_KEY and ANTHROPIC_API_KEY (for the OpenAI/Claude tier).\n"
        "Please update your '.env' file."
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
    TOP_K = int(os.getenv("TOP_K", "3"))
except ValueError:
    TOP_K = 3

try:
    SIMILARITY_CUTOFF = float(os.getenv("SIMILARITY_CUTOFF", "0.7"))
except ValueError:
    SIMILARITY_CUTOFF = 0.7
