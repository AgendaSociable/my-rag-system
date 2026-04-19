import re
from langchain_ollama import ChatOllama
from src.agents.state import AgentState
from src.config import LLM_MODEL, OLLAMA_BASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)

VERIFY_PROMPT = """You check if an answer is well sourced from extracts.

SOURCES:
{context}

ANSWER TO CHECK:
{answer}

Are the main statements of the answer supported by the extracts?
Reply in EXACT format:
VERDICT: YES or NO
REASON: <a short sentence>"""

def verifier_agent(state: AgentState) -> dict:
    answer = state["answer"]
    docs = state["retrieved_docs"]
    
    context = "\n\n".join([f"[source: {i}] {doc.page_content}" for i, doc in enumerate(docs, 1)])
    
    has_citations = bool(re.search(r"\[source:\s*\d+\]|\[Extrait\s*\d+\]]", answer))
    
    prompt = VERIFY_PROMPT.format(context=context, answer=answer)
    response = _llm.invoke(prompt).content
    
    verdict_match = re.search(r"VERDICT:\s*(YES|NO)", response, re.IGNORECASE)
    reason_match = re.search(r"REASON:\s*(.+)", response)
    
    verdict = verdict_match.group(1).upper() == "YES" if verdict_match else "NO"
    reason = reason_match.group(1).strip() if reason_match else "Format invalid"
    
    is_verified = verdict and has_citations
    logger.info(f"[Verifier] Verified={is_verified} | Reason: {reason}")

    
    return {
        "is_verified": is_verified,
        "verification_feedback": reason if not is_verified else "",
        "retry_count": state.get("retry_count", 0) + 1,      
    }