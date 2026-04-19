# tests/demo.py
"""
End-to-end demonstration script for the multi-agent RAG system.
Runs a curated set of questions (including a multi-turn conversation),
captures metrics, and writes a formatted report to demo_results.md.
"""

import time
import re
from datetime import datetime
from pathlib import Path

from src.retrieval.embeddings import get_embeddings
from src.retrieval.vector_store import load_vector_store
from src.retrieval.bm25 import BM25Retriever
from src.retrieval.hybrid import HybridRetriever
from src.agents.supervisor import build_graph
from src.memory.conversation import ConversationMemory
from src.memory.query_rewriter import QueryRewriter
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# ---------------------------------------------------------------------------
# Questions
# ---------------------------------------------------------------------------
# Q1-Q3 : multi-turn conversation on ECS
# Q4-Q10 : independent questions
# Q10 : out-of-scope control question

QUESTIONS = [
    # --- Bloc conversationnel (3 tours) ---
    {
        "id": 1,
        "question": "What is the Entity-Component-System (ECS) pattern and why is it used in game engines?",
        "conversational": True,
        "reset_before": True,   # démarre une nouvelle session
    },
    {
        "id": 2,
        "question": "How does it compare to a traditional object-oriented approach?",
        "conversational": True,
        "reset_before": False,  # continue la session
    },
    {
        "id": 3,
        "question": "Can you give a concrete example of implementing it in a game?",
        "conversational": True,
        "reset_before": False,
    },
    # --- Questions indépendantes ---
    {
        "id": 4,
        "question": "How does a game loop work and what are the differences between fixed and variable timestep?",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 5,
        "question": "Compare different memory management strategies used in game engines and their trade-offs.",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 6,
        "question": "What are the main rendering techniques discussed across these documents?",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 7,
        "question": "How do game engines handle collision detection, from broad-phase to narrow-phase?",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 8,
        "question": "What is double buffering and why is it important for rendering?",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 9,
        "question": "Explain how spatial partitioning structures (quadtrees, octrees, BSP) optimize game performance.",
        "conversational": False,
        "reset_before": True,
    },
    {
        "id": 10,
        "question": "What is the best recipe for chocolate cake?",
        "conversational": False,
        "reset_before": True,
    },
]

# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """
    Rough token estimation without tiktoken.
    Rule of thumb : 1 token ≈ 4 characters for English text.
    """
    return max(1, len(text) // 4)


# ---------------------------------------------------------------------------
# Citation extraction
# ---------------------------------------------------------------------------

def extract_citations(docs: list) -> list[dict]:
    """
    Extract source metadata from retrieved documents.
    Returns a list of dicts with 'source' and 'preview' keys.
    """
    citations = []
    seen = set()
    for doc in docs:
        if not hasattr(doc, "metadata"):
            continue
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", None)
        key = f"{source}:{page}"
        if key in seen:
            continue
        seen.add(key)
        preview = doc.page_content[:120].replace("\n", " ").strip()
        citations.append({
            "source": source,
            "page": page,
            "preview": f"{preview}…",
        })
    return citations


# ---------------------------------------------------------------------------
# Core runner
# ---------------------------------------------------------------------------

def run_demo() -> list[dict]:
    """
    Initialise the RAG pipeline and run all demo questions.
    Returns a list of result dicts.
    """
    print("Initialising RAG pipeline…")
    embeddings = get_embeddings()
    vector_store = load_vector_store(embeddings)
    bm25_retriever = BM25Retriever.from_faiss(vector_store)
    retriever = HybridRetriever(vector_store, bm25_retriever)
    app = build_graph(retriever)
    memory = ConversationMemory(max_turns=5)
    rewriter = QueryRewriter()
    print("Pipeline ready.\n")

    results = []

    for item in QUESTIONS:
        qid = item["id"]
        raw_question = item["question"]

        # Reset memory if required
        if item["reset_before"]:
            memory.clear()

        print(f"[Q{qid}] {raw_question}")

        # Rewrite with context
        standalone = rewriter.rewrite(raw_question, memory)

        initial_state = {
            "question": standalone,
            "reformulated_query": "",
            "retrieved_docs": [],
            "answer": "",
            "is_verified": False,
            "verification_feedback": "",
            "retry_count": 0,
        }

        t_start = time.perf_counter()
        try:
            final_state = app.invoke(initial_state)
            elapsed = time.perf_counter() - t_start
            error = None
        except Exception as e:
            elapsed = time.perf_counter() - t_start
            final_state = {
                "answer": f"ERROR: {e}",
                "is_verified": False,
                "retry_count": 0,
                "retrieved_docs": [],
            }
            error = str(e)
            logger.error(f"Q{qid} failed: {e}")

        answer = final_state.get("answer", "")
        docs = final_state.get("retrieved_docs", [])

        memory.add_turn(raw_question, answer)

        citations = extract_citations(docs)
        prompt_tokens = estimate_tokens(standalone)
        answer_tokens = estimate_tokens(answer)
        total_tokens = prompt_tokens + answer_tokens

        result = {
            "id": qid,
            "raw_question": raw_question,
            "standalone_question": standalone,
            "conversational": item["conversational"],
            "answer": answer,
            "citations": citations,
            "elapsed_s": round(elapsed, 2),
            "prompt_tokens": prompt_tokens,
            "answer_tokens": answer_tokens,
            "total_tokens": total_tokens,
            "is_verified": final_state.get("is_verified", False),
            "retry_count": final_state.get("retry_count", 0),
            "error": error,
        }
        results.append(result)

        status = "✓" if not error else "✗"
        print(f"  {status} {elapsed:.2f}s — ~{total_tokens} tokens — verified: {result['is_verified']}\n")

    return results


# ---------------------------------------------------------------------------
# Markdown report
# ---------------------------------------------------------------------------

def build_markdown(results: list[dict]) -> str:
    """Render the demo results as a readable Markdown report."""

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total_time = sum(r["elapsed_s"] for r in results)
    total_tokens = sum(r["total_tokens"] for r in results)
    verified_count = sum(1 for r in results if r["is_verified"])
    error_count = sum(1 for r in results if r["error"])

    lines = []

    # ── Header ──────────────────────────────────────────────────────────────
    lines += [
        "# 🎮 RAG System — Demo Results",
        "",
        f"> Generated on **{ts}**",
        "",
        "---",
        "",
    ]

    # ── Summary table ────────────────────────────────────────────────────────
    lines += [
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Questions run | {len(results)} |",
        f"| Verified answers | {verified_count} / {len(results)} |",
        f"| Errors | {error_count} |",
        f"| Total time | {total_time:.2f} s |",
        f"| Avg time / question | {total_time / len(results):.2f} s |",
        f"| Total tokens (estimated) | {total_tokens} |",
        f"| Avg tokens / question | {total_tokens // len(results)} |",
        "",
        "---",
        "",
    ]

    # ── Conversation block note ──────────────────────────────────────────────
    lines += [
        "## Questions",
        "",
        "> **Q1 → Q3** form a multi-turn conversation on the ECS pattern.",
        "> **Q4 → Q10** are independent questions.",
        "> **Q10** is an out-of-scope control question.",
        "",
    ]

    # ── Per-question sections ────────────────────────────────────────────────
    for r in results:
        tag = "💬 Conversational" if r["conversational"] else "🔹 Independent"
        verified_badge = "✅ Verified" if r["is_verified"] else "⚠️ Not verified"
        error_badge = f"❌ Error: {r['error']}" if r["error"] else ""

        lines += [
            f"### Q{r['id']} — {r['raw_question']}",
            "",
            f"**Type:** {tag} &nbsp;|&nbsp; **Status:** {verified_badge} {error_badge}",
            "",
        ]

        # Rewritten question (only show when different)
        if r["standalone_question"].strip() != r["raw_question"].strip():
            lines += [
                f"**Rewritten query:** *{r['standalone_question']}*",
                "",
            ]

        # Metrics
        lines += [
            "| Metric | Value |",
            "|--------|-------|",
            f"| Response time | {r['elapsed_s']} s |",
            f"| Prompt tokens (est.) | {r['prompt_tokens']} |",
            f"| Answer tokens (est.) | {r['answer_tokens']} |",
            f"| Total tokens (est.) | {r['total_tokens']} |",
            f"| Retry attempts | {r['retry_count']} |",
            "",
        ]

        # Answer
        lines += [
            "**Answer:**",
            "",
            r["answer"],
            "",
        ]

        # Citations
        if r["citations"]:
            lines += ["**Sources:**", ""]
            for i, c in enumerate(r["citations"], 1):
                page_info = f", p. {c['page']}" if c["page"] is not None else ""
                lines.append(f"{i}. `{c['source']}{page_info}` — *{c['preview']}*")
            lines.append("")
        else:
            lines += ["**Sources:** *No sources retrieved.*", ""]

        lines.append("---")
        lines.append("")

    # ── Footer ───────────────────────────────────────────────────────────────
    lines += [
        "## Notes",
        "",
        "- Token counts are **estimated** (1 token ≈ 4 characters). "
        "Ollama does not expose token counts in this configuration.",
        "- The out-of-scope question (Q10) is intentional: "
        "it validates that the system refuses to hallucinate.",
        "- Multi-turn questions (Q1–Q3) share a sliding-window memory of 5 turns.",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> None:
    output_path = Path("demo_results.md")

    results = run_demo()

    print("Writing report…")
    md = build_markdown(results)
    output_path.write_text(md, encoding="utf-8")
    print(f"Report saved → {output_path.resolve()}")

    # Quick console summary
    total_time = sum(r["elapsed_s"] for r in results)
    total_tokens = sum(r["total_tokens"] for r in results)
    print(f"\nDone. {len(results)} questions — {total_time:.2f}s — ~{total_tokens} tokens")


if __name__ == "__main__":
    main()
