import logging
from typing import List, Tuple
import ollama

from src.config import LLM_MODEL
from src.retrieval.hybrid import HybridRetriever
from src.retrieval.reranker import Reranker
from src.rag.prompt import SYSTEM_PROMPT, build_prompt

logger = logging.getLogger(__name__)

class RAGPipeline:
    def __init__(self, retriever: HybridRetriever, reranker: Reranker = None, model: str = LLM_MODEL):
        self.retriever = retriever
        self.reranker = reranker or Reranker(model=model)
        self.model = model
        logger.info(f"RAGPipeline initialized with model: {self.model}")
    
    def answer(self, question: str, retrieve_k: int = 10, final_k: int = 3) -> dict:
        logger.info(f"Retrieving top {retrieve_k} chunks...")
        _, _, hybrid_results = self.retriever.search(question, k_retriever=retrieve_k, top_k=retrieve_k)
        
        top_chunks = self.reranker.rerank(question, hybrid_results, top_k=final_k)

        user_prompt = build_prompt(question, top_chunks)
        
        logger.info("Generating answer ...")
        response = ollama.chat(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            options={"temperature": 0.2},
        )
        answer = response["message"]["content"]

        return {
            "question" : question,
            "answer" : answer,
            "sources" : top_chunks,
        }