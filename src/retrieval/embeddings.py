from langchain_ollama import OllamaEmbeddings
from src.config import EMBEDDING_MODEL, OLLAMA_BASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def get_embeddings():
    logger.info(f"Initializing OllamaEmbeddings with model: {EMBEDDING_MODEL}")
    return OllamaEmbeddings(model=EMBEDDING_MODEL, base_url=OLLAMA_BASE_URL, num_ctx=2048)