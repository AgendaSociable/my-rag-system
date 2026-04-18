import argparse
from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import load_vector_store
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import Reranker
from src.config import LLM_MODEL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def print_results(title: str, results):
    print(f"\n{'=' * 70}\n{title}\n{'=' * 70}")
    for rank, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "?").split("/")[-1]
        page = doc.metadata.get("page", "?")
        preview = doc.page_content[:200].replace("\n", " ")
        print(f"\n[{rank}] score={score:.4f} | {source} (p.{page})")
        print(f"    {preview}...")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query", type=str, help="Your question")
    parser.add_argument("-k", type=int, default=5, help="Number of results to display")
    parser.add_argument(
        "--pool", type=int, default=20,
        help="How many results each retriever fetches before fusion (default: 20)"
    )
    args = parser.parse_args()

    # Chargement
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    bm25 = BM25Retriever.from_faiss(vector_store)
    hybrid = HybridRetriever(vector_store, bm25)

    # Recherche
    vec_results, bm25_results, hybrid_results = hybrid.search(
        args.query,
        args.pool,
        args.k,
    )
    
    # Reranking
    reranker = Reranker(model= LLM_MODEL)
    reranked_results = reranker.rerank(args.query, hybrid_results, top_k=3)
    

    # Affichage comparatif
    print_results(f"🔵 VECTORIEL (top {args.k})", vec_results)
    print_results(f"🟡 BM25 (top {args.k})", bm25_results)
    print_results(f"🟢 HYBRIDE RRF (top {args.k})", hybrid_results)
    print_results("🔴 RERANKED LLM (top 3)", reranked_results)

    # Résumé : quels chunks sont nouveaux dans l'hybride ?
    vec_ids = {doc.page_content[:100] for doc, _ in vec_results}
    bm25_ids = {doc.page_content[:100] for doc, _ in bm25_results}
    print(f"\n{'=' * 70}")
    print("📊 ANALYSE RRF")
    print(f"{'=' * 70}")
    for rank, (doc, score) in enumerate(hybrid_results, 1):
        doc_id = doc.page_content[:100]
        origin = []
        if doc_id in vec_ids:
            origin.append("VECTORIEL")
        if doc_id in bm25_ids:
            origin.append("BM25")
        source = " + ".join(origin) if origin else "RRF only"
        page = doc.metadata.get("page", "?")
        print(f"[{rank}] p.{page} → trouvé par : {source}")


if __name__ == "__main__":
    main()
