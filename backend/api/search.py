from fastapi import APIRouter

router = APIRouter()

@router.get("/search")
def search_pdf(question: str):

    from services.embedding_service import create_embeddings
    from vector_store.faiss_store import search
    from database.chunk_store import load_chunks

    query_embedding = create_embeddings([question])

    indices = search(query_embedding)

    chunks = load_chunks()

    results = []

    for i in indices[0]:
        if i < len(chunks):
            results.append(chunks[i])

    return {
        "question": question,
        "answer": results
    }