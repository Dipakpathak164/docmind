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

# Check required API keys unless we are executing unit tests
missing_keys = []
if not OPENAI_API_KEY:
    missing_keys.append("OPENAI_API_KEY")
if not ANTHROPIC_API_KEY:
    missing_keys.append("ANTHROPIC_API_KEY")

if missing_keys and not IS_TESTING:
    raise ValueError(
        f"Missing required environment variables: {', '.join(missing_keys)}.\n"
        f"Please create a '.env' file in the project root directory based on '.env.example' "
        f"and set these API keys before running the application."
    )

# Assign dummy keys in testing environment if not present
if IS_TESTING:
    OPENAI_API_KEY = OPENAI_API_KEY or "mock-openai-key"
    ANTHROPIC_API_KEY = ANTHROPIC_API_KEY or "mock-anthropic-key"

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
