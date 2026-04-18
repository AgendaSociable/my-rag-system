import json
import logging
from typing import List, Tuple
import ollama
from src.config import LLM_MODEL

logger = logging.getLogger(__name__)


class Reranker:
    def __init__(self, model: str = LLM_MODEL):
        self.model = model
        logger.info(f"Reranker initialized with model: {self.model}")

    def rerank(self, query: str, chunks: List[Tuple], top_k: int = 3) -> List[Tuple]:
        if not chunks:
            return []

        chunks_text = ""
        for i, (doc, score) in enumerate(chunks):
            chunks_text += f"\n[{i}] {doc.page_content[:300]}\n"

        prompt = f"""Rank the following chunks by relevance to the query.

Query: {query}

Chunks:{chunks_text}

Return ONLY a JSON object of the form: {{"ranking": [2, 0, 4, 1, 3]}}
where the list contains the chunk indices ordered from MOST to LEAST relevant."""

        logger.info(f"Reranking {len(chunks)} chunks with LLM: {self.model}")

        response = ollama.chat(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            format="json",
            options={"temperature": 0},
        )

        raw = response["message"]["content"].strip()
        logger.info(f"LLM raw response: {raw}")

        ranked_indices = self._parse_response(raw, len(chunks))
        return [chunks[i] for i in ranked_indices[:top_k]]

    def _parse_response(self, raw: str, num_chunks: int) -> List[int]:
        try:
            data = json.loads(raw)
            indices = data.get("ranking", [])

            # garde seulement les indices valides et uniques
            seen = set()
            valid = []
            for i in indices:
                if isinstance(i, int) and 0 <= i < num_chunks and i not in seen:
                    valid.append(i)
                    seen.add(i)

            # complète avec les indices manquants (au cas où le LLM en oublie)
            missing = [i for i in range(num_chunks) if i not in seen]
            return valid + missing

        except Exception as e:
            logger.warning(f"Failed to parse LLM response: {e}. Using original order.")
            return list(range(num_chunks))
