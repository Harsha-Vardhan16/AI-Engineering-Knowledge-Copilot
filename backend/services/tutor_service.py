import re
from typing import Dict, Any, List
from services.embedding_service import create_embeddings
from vector_store.faiss_store import search, get_total_vectors
from database.db import get_chunks_by_indices, get_all_chunks_raw
from services.llm_service import generate_llm_response


def answer_question(question: str, top_k: int = 4) -> Dict[str, Any]:
    """
    RAG Tutor Query: Retrieves relevant chunks from FAISS, extracts genuine citations
    (document name and page number), and generates a step-by-step engineering answer.
    """
    total_vectors = get_total_vectors()
    if total_vectors == 0:
        return {
            "question": question,
            "answer": "No course documents have been indexed yet. Please upload an engineering PDF or ingest sample course materials from the Documents tab.",
            "citations": [],
            "has_context": False
        }

    # Embed query and search FAISS
    query_emb = create_embeddings([question])
    indices = search(query_emb, k=top_k)

    if indices is None or len(indices) == 0 or len(indices[0]) == 0:
        return {
            "question": question,
            "answer": "I could not locate relevant material in the current course notes. Please check the topic keywords or upload relevant notes.",
            "citations": [],
            "has_context": False
        }

    valid_indices = [int(i) for i in indices[0] if i >= 0]
    matched_chunks = get_chunks_by_indices(valid_indices)

    if not matched_chunks:
        return {
            "question": question,
            "answer": "No direct matches found in the uploaded documents.",
            "citations": [],
            "has_context": False
        }

    # Build genuine citations and context
    context_blocks = []
    citations = []
    seen_citations = set()

    for chunk in matched_chunks:
        fn = chunk.get("filename", "Course Note")
        page = chunk.get("page_number", 1)
        content = chunk.get("content", "").strip()

        cit_key = f"{fn}#p{page}"
        if cit_key not in seen_citations:
            seen_citations.add(cit_key)
            # Create a clean excerpt
            excerpt = content[:200].replace("\n", " ") + ("..." if len(content) > 200 else "")
            citations.append({
                "filename": fn,
                "page": page,
                "excerpt": excerpt
            })

        context_blocks.append(f"--- [Document: {fn} | Page: {page}] ---\n{content}")

    context_str = "\n\n".join(context_blocks)

    system_prompt = (
        "You are 'EngineeringAI', a patient, senior engineering professor and AI tutor. "
        "Your mission is to explain complex engineering concepts simply, clearly, and step by step. "
        "Ground your answer STRICTLY in the provided course notes. "
        "Explicitly cite the source document and page number when explaining key facts. "
        "If the information is not present in the notes, state honestly that the uploaded notes do not cover it."
    )

    prompt = f"""
Course Notes Context:
{context_str}

Student Question:
{question}

Provide an intuitive, step-by-step engineering explanation. Mention genuine citations ([Filename, Page X]) wherever appropriate:
"""

    fallback_answer = (
        f"Based on your course notes ({', '.join(seen_citations)}):\n\n"
        + matched_chunks[0].get("content", "")[:500]
        + "\n\n[Note: Real-time synthesis is displaying direct excerpts from your verified course materials.]"
    )

    answer = generate_llm_response(prompt, system=system_prompt, fallback_text=fallback_answer)

    return {
        "question": question,
        "answer": answer,
        "citations": citations,
        "has_context": True
    }
