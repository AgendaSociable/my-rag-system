"""Hybrid retrieval: BM25 + vector search fused with Reciprocal Rank Fusion."""

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
    """Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).

    RRF score for a document d:  Σ 1 / (k + rank(d))

    Args:
        ranked_lists: Each inner list is ``[(document, score), …]`` sorted
                      by relevance descending.
        k: RRF smoothing constant. Higher values reduce the impact of
           top-ranked documents.

    Returns:
        Single merged list of ``(document, rrf_score)`` sorted descending.
    """
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
    """Combine FAISS vector search and BM25 via RRF fusion.

    Args:
        vector_store: Loaded FAISS index.
        bm25_retriever: Initialised BM25Retriever over the same corpus.
    """
    def __init__(self, vector_store: FAISS, bm25_retriever: BM25Retriever):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever
        
    def search(
        self, query: str, k_retriever: int = 20, top_k: int = 5
        ) -> Tuple[List[Tuple[Document, float]], List[Tuple[Document, float]], List[Tuple[Document, float]]]:
        """Run hybrid search and return top results from each strategy.

        Args:
            query: User query string.
            k_retriever: Number of candidates fetched from each retriever
                         before fusion.
            top_k: Number of results returned per strategy.

        Returns:
            Three lists of ``(document, score)`` tuples:
            ``(vector_results, bm25_results, hybrid_results)``,
            each truncated to *top_k*.
        """
        
        logger.info(f"Vectoriel search (k={k_retriever})...")
        vec_resutls = self.vector_store.similarity_search_with_score(query, k=k_retriever)
        
        logger.info(f"BM25 search (k={k_retriever})...")
        bm25_results = self.bm25_retriever.search(query, k_retriever)
        
        logger.info("Apply RRF fusion")
        hybrid_results = rank_fusion([vec_resutls, bm25_results])
        
        return vec_resutls[:top_k], bm25_results[:top_k], hybrid_results[:top_k] 