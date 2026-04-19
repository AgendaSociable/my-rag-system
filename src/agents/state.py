"""Shared state passed between agents in the LangGraph pipeline."""

from typing import Tuple, TypedDict, List
from langchain_core.documents import Document

class AgentState(TypedDict):
    """State flowing through the multi-agent graph.

    Attributes:
        question: Original user question.
        reformulated: Query rewritten by the retriever agent for better recall.
        retrieved_docs: Documents returned by the hybrid retriever.
        answer: Answer produced by the synthesizer.
        is_verified: Whether the verifier accepted the answer.
        verification_feedback: Verifier explanation when the answer is rejected.
        retry_count: Number of synthesize/verify loops already executed.
    """
    question: str
    reformulated: str
    retrieved_docs: List[Document]
    answer: str
    is_verified: bool
    verification_feedback: str
    retry_count: int