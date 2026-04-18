from pathlib import Path
from typing import List
from tqdm import tqdm
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings
from langchain_community.vectorstores import FAISS
from src.config import VECTOR_STORE_DIR, MAX_CHARS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def build_vector_store(
    embeddings: Embeddings,
    documents: List[Document],
    persist_dir: Path = VECTOR_STORE_DIR,
    batch_size: int = 32,
) -> FAISS:
    if not documents:
        raise ValueError("No documents provided to build the vector store.")

    logger.info(f"Building FAISS index from {len(documents)} chunks.")

    texts = [doc.page_content for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    filtered_texts = [(text, meta) for text, meta in zip(texts, metadatas) if len(text) <= MAX_CHARS ] 
    skipped = len(texts) - len(filtered_texts)
    if skipped:
        logger.warning(f"Skipped {skipped} chunks that exceeded the maximum character limit of {MAX_CHARS}.")
    
    texts = [text for text, _ in filtered_texts]
    metadatas = [meta for _, meta in filtered_texts]

    all_embeddings = []
    for i in tqdm(range(0, len(texts), batch_size), desc="Embedding chunks"):
        batch = texts[i : i + batch_size]
        all_embeddings.extend(embeddings.embed_documents(batch))

    logger.info("Embeddings computed, building FAISS index...")

    text_embedding_pairs = list(zip(texts, all_embeddings))
    vector_store = FAISS.from_embeddings(
        text_embeddings=text_embedding_pairs,
        embedding=embeddings,
        metadatas=metadatas,
    )

    persist_dir.mkdir(parents=True, exist_ok=True)
    vector_store.save_local(str(persist_dir))
    logger.info(f"Vector store saved to {persist_dir}")
    return vector_store


def load_vector_store(
    embeddings: Embeddings,
    persist_dir: Path = VECTOR_STORE_DIR,
) -> FAISS:
    if not persist_dir.exists():
        raise FileNotFoundError(f"No vector store found at {persist_dir}.")

    logger.info(f"Loading FAISS index from {persist_dir}")
    return FAISS.load_local(
        str(persist_dir), embeddings, allow_dangerous_deserialization=True
    )
