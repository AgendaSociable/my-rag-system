from rank_bm25 import BM25Okapi
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def _tokenize(text: str) -> List[str]:
    return text.lower().split()

class BM25Retriever:
    def __init__(self,documents: List[Document]):
        if not documents:
            raise ValueError("No documents provided for BM25 index.")
        self.documents = documents
        tokenized_corpus = [ _tokenize(doc.page_content) for doc in documents ]
        self.bm25 = BM25Okapi(tokenized_corpus)
        logger.info(f"BM25 index built on {len(documents)} documents.")
    
    @classmethod
    def from_faiss(cls, vector_store: FAISS) -> 'BM25Retriever':
        docs = list(vector_store.docstore._dict.values())
        return cls(docs)
        
    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        scores = self.bm25.get_scores(_tokenize(query))
        top_idx = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [(self.documents[i], scores[i]) for i in top_idx]