from typing import Tuple, TypedDict, List
from langchain_core.documents import Document

class AgentState(TypedDict):
    question: str
    reformulated_query: str
    retrieved_docs: List[Tuple[Document, float]]
    answer: str
    is_verified: bool
    verification_feedback: str
    retry_count: int