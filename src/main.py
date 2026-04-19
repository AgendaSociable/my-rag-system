from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import load_vector_store
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.agents.supervisor import build_graph


def main():
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    bm25_retriever = BM25Retriever.from_faiss(vector_store)
    retriever = HybridRetriever(vector_store, bm25_retriever)

    app = build_graph(retriever)

    while True:
        question = input("\nQuestion (or 'quit'): ").strip()
        if question.lower() in {"quit", "exit"}:
            break

        initial_state = {
            "question": question,
            "reformulated_query": "",
            "retrieved_docs": [],
            "answer": "",
            "is_verified": False,
            "verification_feedback": "",
            "retry_count": 0,
        }

        final_state = app.invoke(initial_state)
        
        print(f"VERIFIED: {final_state['is_verified']}")
        print(f"FEEDBACK: {final_state['verification_feedback']}")
        print(f"ATTEMPTS: {final_state['retry_count']}")


        print("\n" + "=" * 60)
        print(f"ANSWER:\n{final_state['answer']}")
        print(f"\nVERIFIED: {final_state['is_verified']}")
        print(f"ATTEMPTS: {final_state['retry_count']}")


if __name__ == "__main__":
    main()
