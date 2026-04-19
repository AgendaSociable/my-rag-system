"""End-to-end RAG pipeline: hybrid retrieval → LLM rerank → answer generation."""
from typing import List, Tuple
import ollama
from src.exceptions import LLMError, EmptyContextError
from src.config import LLM_MODEL
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import Reranker
from src.rag.prompt import SYSTEM_PROMPT, build_prompt
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

class RAGPipeline:
    """End-to-end RAG pipeline: retrieve → rerank → generate.

    Args:
        retriever: Hybrid retriever combining FAISS and BM25.
        reranker: Optional reranker. A default one is built from *model*
                  if omitted.
        model: Ollama model name used for generation (and for the default
               reranker).
    """

    def __init__(self, retriever: HybridRetriever, reranker: Reranker = None, model: str = LLM_MODEL):
        self.retriever = retriever
        self.reranker = reranker or Reranker(model=model)
        self.model = model
        logger.info(f"RAGPipeline initialized with model: {self.model}")
    
    def answer(self, question: str, retrieve_k: int = 10, final_k: int = 3) -> dict:
        """Answer a question with hybrid retrieval, reranking and generation.

        Args:
            question: User question.
            retrieve_k: Number of chunks fetched by the hybrid retriever.
            final_k: Number of chunks kept after reranking and fed to the LLM.

        Returns:
            Dict with keys:
                - ``question``: the original question.
                - ``answer``: the LLM answer.
                - ``sources``: the ``(document, score)`` tuples actually cited.

        Raises:
            EmptyContextError: No chunks were retrieved for the question.
            LLMError: The Ollama call failed.
        """
        logger.info(f"Retrieving top {retrieve_k} chunks...")
        _, _, hybrid_results = self.retriever.search(question, k_retriever=retrieve_k, top_k=retrieve_k)
        
        if not hybrid_results:
            logger.warning(f"No chunks retrieved for question: {question!r}")
            raise EmptyContextError("No relevant chunks found for this question.")
        
        top_chunks = self.reranker.rerank(question, hybrid_results, top_k=final_k)

        user_prompt = build_prompt(question, top_chunks)
        
        logger.info("Generating answer ...")
        try:
            response = ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                options={"temperature": 0.2},
            )
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise LLMError(f"LLM generation failed: {e}") from e
        
        answer = response["message"]["content"]

        return {
            "question" : question,
            "answer" : answer,
            "sources" : top_chunks,
        }