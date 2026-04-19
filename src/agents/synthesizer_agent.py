from langchain_ollama import ChatOllama
from src.agents.state import AgentState
from src.rag.prompt import build_contexte
from src.config import LLM_MODEL, OLLAMA_BASE_URL
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

_llm = ChatOllama(model=LLM_MODEL, base_url=OLLAMA_BASE_URL)

SYNTHESIS_PROMPT = """You are an expert in game programming. Answer the question based ONLY on the excerpts provided.

RULES:
- Cite each statement using [source: N] where N is the extract number.
- If the information is not in the excerpts, say "I can’t find this information in the sources provided."
- Be precise and technical.

EXTRACTS :
{context}

QUESTION : {question}

RESPONSE :"""

def synthesizer_agent(state: AgentState) -> dict:
    docs = state["retrieved_docs"]
    question = state["question"]
    feedback = state.get("verification_feedback", "")
    
    chunks = [(doc, 0.0) for doc in docs]
    context = build_contexte(chunks)
     
    prompt = SYNTHESIS_PROMPT.format(context=context, question=question)
    
    if feedback:
        prompt += (f"\n\nWARNING - previous feedback : {feedback}\n"
                   "Please improve your answer accordingly, ensuring every claim is properly cited.")
    
    logger.info("[Synthesizer] generating answer...")
    response = _llm.invoke(prompt)
    answer = response.content.strip()
    
    logger.info(f"[Synthesizer] Answer generated ({len(answer)} chars)")
    
    return {
        "answer": answer,
    }