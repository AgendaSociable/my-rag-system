from typing import List, Tuple, Dict
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from src.retrieval.bm25 import BM25Retriever
from src.config import K_CONSTANT
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

def rank_fusion(
    ranked_lists: List[List[Tuple[Document, float]]],
    k: int = K_CONSTANT
    ) -> List[Tuple[Document, float]]:
    rrf_scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}
    
    for ranked_list in ranked_lists:
        for rank, (doc, score) in enumerate(ranked_list, 1):
            doc_id = doc.page_content[:100]
            rrf_scores[doc_id] = rrf_scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            doc_map[doc_id] = doc
        
    sorted_ids = sorted(rrf_scores.keys(), key=lambda id: rrf_scores[id], reverse=True)
    return [(doc_map[doc_id], rrf_scores[doc_id]) for doc_id in sorted_ids]

class HybridRetriever:
    def __init__(self, vector_store: FAISS, bm25_retriever: BM25Retriever):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever
        
    def search(
        self, query: str, k_retriever: int = 20, top_k: int = 5
        ) -> Tuple[List[Tuple[Document, float]], List[Tuple[Document, float]], List[Tuple[Document, float]]]:
        
        logger.info(f"Vectoriel search (k={k_retriever})...")
        vec_resutls = self.vector_store.similarity_search_with_score(query, k=k_retriever)
        
        logger.info(f"BM25 search (k={k_retriever})...")
        bm25_results = self.bm25_retriever.search(query, k_retriever)
        
        logger.info("Apply RRF fusion")
        hybrid_results = rank_fusion([vec_resutls, bm25_results])
        
        return vec_resutls[:top_k], bm25_results[:top_k], hybrid_results[:top_k] 