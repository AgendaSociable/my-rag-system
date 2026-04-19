"""Central configuration for the RAG system.

Values are loaded from environment variables (.env) with sensible defaults.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


PROJECT_DIR: Path = Path(__file__).parent.parent
DATA_DIR: Path = PROJECT_DIR / "data"
INDEX_DIR: Path = PROJECT_DIR / "faiss_index"
VECTOR_STORE_DIR: Path = PROJECT_DIR / "vector_store"

CHUNK_SIZE: int = 500
CHUNK_OVERLAP: int = 50
MAX_CHARS: int = 1000

SUPPORTED_TYPES: list[str] = [".pdf", ".md", ".txt"]

MAX_RETRIES: int = 2

OLLAMA_BASE_URL: str | None = os.getenv("OLLAMA_BASE_URL")
LLM_MODEL: str | None = os.getenv("LLM_MODEL")
EMBEDDING_MODEL: str | None = os.getenv("EMBEDDING_MODEL")

TOP_K: int = 5
K_CONSTANT: int = 60  # RRF