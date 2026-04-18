from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredMarkdownLoader,
    TextLoader,
)
from langchain_core.documents import Document
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_pdf(path: Path) -> List[Document]:
    logger.info(f"Loading PDF document from {path.name}")
    loader = PyPDFLoader(str(path)).load()
    logger.info(f"Loaded {len(loader)} pages")
    return loader     

def load_markdown(path: Path) -> List[Document]:
    logger.info(f"Loading Markdown document from {path.name}")
    loader = UnstructuredMarkdownLoader(str(path)).load()
    return loader

def load_text(path: Path) -> List[Document]:
    logger.info(f"Loading Text document from {path.name}")
    loader = TextLoader(str(path), encoding="utf-8").load()
    return loader

LOADER = {
    ".pdf": load_pdf,
    ".md": load_markdown,
    ".txt": load_text,
}