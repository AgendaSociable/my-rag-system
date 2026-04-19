class RAGException(Exception):
    """Base exception for the RAG system."""


class DocumentLoadError(RAGException):
    """Raised when a document cannot be loaded or parsed."""


class UnsupportedFormatError(RAGException):
    """Raised when a file format is not supported."""


class LLMError(RAGException):
    """Raised when the LLM call fails (API down, timeout, bad response)."""


class EmptyContextError(RAGException):
    """Raised when retrieval returns no usable chunks."""