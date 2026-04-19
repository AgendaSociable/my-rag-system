"""Low-level document loaders for PDF, Markdown and plain-text files."""

from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_core.documents import Document
from src.exceptions import DocumentLoadError
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_pdf(path: Path) -> List[Document]:
    """Load a PDF file into a list of Documents.
     Args:
        path: Absolute or relative path to the PDF file.

    Returns:
        List of Documents, one per page.

    Raises:
        DocumentLoadError: If the file cannot be parsed by PyPDF.
    """
    logger.info(f"Loading PDF document from {path.name}")
    try:
        loader = PyPDFLoader(str(path)).load()
    except Exception as e:
        logger.error(f"Failed to load PDF {path.name}: {e}")
        raise DocumentLoadError(f"Failed to load PDF document from {path.name}") from e
    logger.info(f"Loaded {len(loader)} pages")
    return loader     

def load_markdown(path: Path) -> List[Document]:
    """Load a Markdown file into a list of Documents.
    Args:
        path: Absolute or relative path to the Markdown file.

    Returns:
        List of Documents (usually one).

    Raises:
        DocumentLoadError: If the file cannot be parsed.
    """
    logger.info(f"Loading Markdown document from {path.name}")
    try:
        loader = UnstructuredMarkdownLoader(str(path)).load()
    except Exception as e:
        logger.error(f"Failed to load Markdown {path.name}: {e}")
        raise DocumentLoadError(f"Failed to load Markdown document from {path.name}") from e
    return loader

def load_text(path: Path) -> List[Document]:
    """Load a Text file into a list of Documents.
     Args:
        path: Absolute or relative path to the text file.

    Returns:
        List of Documents (usually one).

    Raises:
        DocumentLoadError: If the file cannot be read (encoding error, etc.).
    """
    logger.info(f"Loading Text document from {path.name}")
    try:
        loader = TextLoader(str(path), encoding="utf-8").load()
    except Exception as e:
        logger.error(f"Failed to load Text {path.name}: {e}")
        raise DocumentLoadError(f"Failed to load Text document from {path.name}") from e
    return loader

LOADER = {
    ".pdf": load_pdf,
    ".md": load_markdown,
    ".txt": load_text,
}