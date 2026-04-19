from functools import partial
from langgraph.graph import StateGraph, END
from src.agents.state import AgentState
from src.agents.retriever_agent import retriever_agent
from src.agents.synthesizer_agent import synthesizer_agent
from src.agents.verifier_agent import verifier_agent
from src.config import MAX_RETRIES

def should_continue(state: AgentState) -> str:
    if state["is_verified"]:
        return "end"
    if state["retry_count"] >= MAX_RETRIES:
        return "end"
    return "retry"

def build_graph(retriever):
    graph = StateGraph(AgentState)
    
    graph.add_node("retriever", partial(retriever_agent, retriever=retriever))
    graph.add_node("synthesizer", synthesizer_agent)
    graph.add_node("verifier", verifier_agent)
    
    graph.set_entry_point("retriever")
    graph.add_edge("retriever", "synthesizer")
    graph.add_edge("synthesizer", "verifier")
    
    graph.add_conditional_edges(
        "verifier",
        should_continue,
        {
            "end": END,
            "retry": "synthesizer",
        },
    )
    
    return graph.compile()