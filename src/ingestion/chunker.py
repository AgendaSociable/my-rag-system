"""Splits loaded Documents into smaller overlapping chunks."""

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.config import CHUNK_SIZE, CHUNK_OVERLAP
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def chunk_documents(
    documents: List[Document], 
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP
) -> List[Document]:
    """Split documents into overlapping chunks and assign a chunk_id.

    Args:
        documents: Raw documents produced by a loader.
        chunk_size: Maximum number of characters per chunk.
        chunk_overlap: Number of characters shared between consecutive chunks.

    Returns:
        List of chunks, each with a ``chunk_id`` added to its metadata.
    """
    splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    chunks = splitter.split_documents(documents)
    
    for i, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = i
    
    logger.info(f"Split into {len(chunks)} chunks")
    return chunks