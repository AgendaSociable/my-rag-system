from typing import List, Tuple

SYSTEM_PROMPT = """You are a helpful assistant specialized in game programming.
Answer the user's question using ONLY the provided context and be polite.
If the context doesn't contain the answer, say so clearly.

IMPORTANT: Cite your sources inline using this exact format: [source: filename, p.X]
Place the citation right after the information it supports."""

def build_contexte(chunks: List[Tuple]) -> str:
    context_parts = []
    for i, (doc, score) in enumerate(chunks, 1):
        source = doc.metadata.get("source","unknown")
        page = doc.metadata.get("page","?")
        context_parts.append(f'[Chunk {i} (source: {source}, page: {page})]\n{doc.page_content}\n')
    
    return "\n\n---\n\n".join(context_parts)

def build_prompt(question: str, chunks: List[Tuple]) -> str:
    context = build_contexte(chunks)
    return f"""
    Context: {context} 
    --- 
    Question: {question} 
    --- 
    Answer (remember to cite sources inline like [source: filename, p.X]):"""
