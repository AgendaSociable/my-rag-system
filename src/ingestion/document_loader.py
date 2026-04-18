from mimetypes import suffix_map
from pathlib import Path
from typing import List

from langchain_core.documents import Document

from src.config import SUPPORTED_TYPES
from src.ingestion.chunker import chunk_documents
from src.ingestion.loaders import LOADER
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class DocumentLoader:
    def __init__(self, supported_types: set = SUPPORTED_TYPES):
        self.supported_types = supported_types
        
    def load_file(self, path: Path) -> List[Document]:
        if not path.exists():
            raise FileNotFoundError(f"File {path} not found.")
        
        extension = path.suffix.lower()
        if extension not in self.supported_types:
            raise ValueError(f"Unsupported file type: {extension}"
                             f" Supported types: {self.supported_types}")
        
        loader_func = LOADER[extension]
        docs = loader_func(path)
        
        for doc in docs:
            doc.metadata["source"] = path.name
        
        return docs
    
    def load_dir(self, dir_path: Path) -> List[Document]:
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            raise NotADirectoryError(f"{dir_path} is not a directory.")
        
        logger.info(f"Loading documents from directory: {dir_path}")
        all_docs: List[Document] = []
        
        for file_path in dir_path.iterdir():
            if file_path.suffix.lower() in self.supported_types:
                try:
                    docs = self.load_file(file_path)
                    all_docs.extend(docs)
                except Exception as e:
                    logger.error(f"Error loading {file_path.name}: {e}")
        
        logger.info(f"Loaded {len(all_docs)} documents from {dir_path}")
        return chunk_documents(all_docs)