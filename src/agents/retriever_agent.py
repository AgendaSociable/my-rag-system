"""Retriever agent: reformulates the query and runs hybrid search."""

from langchain_ollama import ChatOllama
from src.agents.state import AgentState
from src.retrieval.hybrid import HybridRetriever
from src.config import LLM_MODEL, OLLAMA_BASE_URL, TOP_K
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)

REFORMULATION_PROMPT = """You are an assistant who reformulates the questions to improve documentary research.
Rewrite the question below in a clearer version rich in technical keywords.
Reply ONLY with the question rephrased, without explanation.

Original question : {question}

Reformulated question :"""

def retriever_agent(state: AgentState, retriever: HybridRetriever) -> dict:
    """Reformulate the user question and retrieve relevant documents.

    Args:
        state: Current agent state (must contain ``question``).
        retriever: Hybrid retriever used for the search.

    Returns:
        Partial state update with keys ``reformulated`` and ``retrieved_docs``.
    """
    question = state["question"]
    logger.info(f"[Retriever] question: {question}")
    
    prompt = REFORMULATION_PROMPT.format(question=question)
    response = _llm.invoke(prompt)
    reformulated = response.content.strip()
    logger.info(f"[Retriever] reformulated: {reformulated}")
    
    _, _, hybrid_results = retriever.search(reformulated, top_k=TOP_K)
    docs = [doc for doc, _score in hybrid_results]

    logger.info(f"[Retriever] retrieved {len(docs)} docs")
    
    return {
        "reformulated": reformulated,
        "retrieved_docs": docs,
    }
