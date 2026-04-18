from pathlib import Path

PROJECT_DIR = Path(__file__).parent
DATA_DIR = PROJECT_DIR / "data"
INDEX_DIR = PROJECT_DIR / "faiss_index"

CHUNK_SIZE = 800
CUNK_OVERLAP = 200
SUPPORTED_TYPES = [".pdf", ".md", ".txt"]

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = "llama3.2:3b"

TOP_K = 5