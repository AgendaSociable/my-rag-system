"""Rewrites a follow-up question into a standalone one using chat history."""

from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from src.config import LLM_MODEL
from src.memory.conversation import ConversationMemory
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

REWRITE_PROMPT = """You are a query rewriter for a RAG system.

Given a conversation history and a new user question, rewrite the question so it is fully **standalone** (understandable without the history).

Rules:
- If the question is already standalone, return it UNCHANGED.
- Resolve pronouns and references ("it", "that", "this topic", "and for X?").
- Keep the same language as the user.
- Return ONLY the rewritten question, no explanation.

Conversation history:
{history}

New question: {question}

Standalone question:"""


class QueryRewriter:
    """Rewrite context-dependent questions into standalone queries.

    Uses a deterministic (temperature=0) LLM call. When the conversation
    memory is empty, the original question is returned as-is to save a
    round-trip.
    """
    def __init__(self):
        self.llm = ChatOllama(model=LLM_MODEL, temperature=0)
        self.prompt = ChatPromptTemplate.from_template(REWRITE_PROMPT)

    def rewrite(self, question: str, memory: ConversationMemory) -> str:
        """Return a standalone version of *question* given past turns.

        Args:
            question: Latest user question, possibly referring to prior turns.
            memory: Conversation memory holding the recent Q/A exchanges.

        Returns:
            A self-contained question. Equal to *question* when memory is empty.
        """
        if not memory.get_history():
            logger.info("[Rewriter] No history, returning original question.")
            return question

        chain = self.prompt | self.llm
        result = chain.invoke({
            "history": memory.format_for_prompt(),
            "question": question,
        })
        rewritten = result.content.strip()
        logger.info(f"[Rewriter] '{question}' → '{rewritten}'")
        return rewritten
