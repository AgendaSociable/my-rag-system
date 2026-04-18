import argparse
from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import load_vector_store
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import Reranker
from src.rag.generator import RAGPipeline
from src.config import LLM_MODEL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str, help="Your question")
    parser.add_argument("--retrieve-k", type=int, default=10,
                        help="Chunks before reranking (default: 10)")
    parser.add_argument("--final-k", type=int, default=3,
                        help="Chunks after reranking (default: 3)")
    parser.add_argument("--show-sources", action="store_true",
                        help="Display the source chunks used")
    args = parser.parse_args()

    logger.info("Loading embeddings and vector store...")
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    bm25 = BM25Retriever.from_faiss(vector_store)
    retriever = HybridRetriever(vector_store, bm25)

    reranker = Reranker(model=LLM_MODEL)
    rag = RAGPipeline(retriever, reranker)

    result = rag.answer(
        args.question,
        retrieve_k=args.retrieve_k,
        final_k=args.final_k,
    )

    print("\n" + "=" * 70)
    print(f"QUESTION: {result['question']}")
    print("=" * 70)
    print(f"\nANSWER:\n{result['answer']}\n")

    if args.show_sources:
        print("=" * 70)
        print("SOURCES USED:")
        print("=" * 70)
        for i, (doc, score) in enumerate(result["sources"], 1):
            src = doc.metadata.get("source", "?").split("/")[-1]
            page = doc.metadata.get("page", "?")
            preview = doc.page_content[:200].replace("\n", " ")
            print(f"\n[{i}] {src} (p.{page}) — score={score:.4f}")
            print(f"    {preview}...")


if __name__ == "__main__":
    main()
