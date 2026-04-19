import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


PROJECT_DIR = Path(__file__).parent.parent
DATA_DIR = PROJECT_DIR / "data"
INDEX_DIR = PROJECT_DIR / "faiss_index"
VECTOR_STORE_DIR = PROJECT_DIR / "vector_store"


CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MAX_CHARS = 1000
SUPPORTED_TYPES = [".pdf", ".md", ".txt"]

MAX_RETRIES = 2

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL")


TOP_K = 5
K_CONSTANT = 60
