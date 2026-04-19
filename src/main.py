from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import load_vector_store
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.agents.supervisor import build_graph
from src.memory.conversation import ConversationMemory
from src.memory.query_rewriter import QueryRewriter
from src.exceptions import RAGException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main() -> None:
    """Interactive CLI entrypoint for the RAG system."""
    try:
        embeddings = get_embeddings()
        vector_store = load_vector_store(embeddings)
        bm25_retriever = BM25Retriever.from_faiss(vector_store)
        retriever = HybridRetriever(vector_store, bm25_retriever)
        app = build_graph(retriever)
        memory = ConversationMemory(max_turns=5)
        rewriter = QueryRewriter()
    except Exception as e:
        logger.critical(f"Failed to initialize RAG system: {e}", exc_info=True)
        print(f"Fatal error during init: {e}")
        return

    while True:
        try:
            question = input("\nQuestion (or 'quit' / 'reset'): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nBye!")
            break

        if not question:
            continue
        if question.lower() in {"quit", "exit"}:
            break
        if question.lower() == "reset":
            memory.clear()
            print("Memory cleared.")
            continue

        try:
            standalone_question = rewriter.rewrite(question, memory)

            initial_state = {
                "question": standalone_question,
                "reformulated_query": "",
                "retrieved_docs": [],
                "answer": "",
                "is_verified": False,
                "verification_feedback": "",
                "retry_count": 0,
            }
            final_state = app.invoke(initial_state)

            memory.add_turn(question, final_state["answer"])

            print("\n" + "=" * 60)
            print(f"ANSWER:\n{final_state['answer']}")
            print(f"\nVERIFIED: {final_state['is_verified']}")
            print(f"ATTEMPTS: {final_state['retry_count']}")
            print(f"HISTORY SIZE: {len(memory.get_history())} turns")

        except RAGException as e:
            logger.error(f"RAG error: {e}")
            print(f"Error:  {e}")
        except Exception as e:
            logger.exception(f"Unexpected error: {e}")
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
