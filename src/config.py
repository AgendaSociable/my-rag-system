from pathlib import Path

PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
INDEX_DIR = PROJECT_DIR / "faiss_index"
VECTOR_STORE_DIR = PROJECT_DIR / "vector_store"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_CHARS = 1000
SUPPORTED_TYPES = [".pdf", ".md", ".txt"]

OLLAMA_BASE_URL = "http://localhost:11434"
EMBEDDING_MODEL = "all-minilm"
LLM_MODEL = "llama3.2:3b"

TOP_K = 5
K_CONSTANT = 60