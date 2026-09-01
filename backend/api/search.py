from fastapi import APIRouter

router = APIRouter()


@router.get("/search")
def search_pdf(question: str):

    # ===============================
    # Import required functions
    # ===============================

    from services.embedding_service import create_embeddings
    from vector_store.faiss_store import search
    from database.chunk_store import load_chunks

    # Llama through Ollama
    from langchain_ollama import ChatOllama


    # ===============================
    # Step 1: Convert question to embedding
    # ===============================

    query_embedding = create_embeddings([question])


    # ===============================
    # Step 2: Search FAISS
    # ===============================

    indices = search(query_embedding)


    # ===============================
    # Step 3: Load stored chunks
    # ===============================

    chunks = load_chunks()


    # ===============================
    # Step 4: Get relevant chunks
    # ===============================

    results = []

    for i in indices[0]:

        if i < len(chunks):

            results.append(chunks[i])


    # ===============================
    # Step 5: Combine retrieved chunks
    # ===============================

    context = "\n\n".join(results)


    # ===============================
    # Step 6: Connect Llama 3.2
    # ===============================

    llm = ChatOllama(
        model="llama3.2:latest",
        temperature=0
    )


    # ===============================
    # Step 7: Create RAG prompt
    # ===============================

    prompt = f"""
You are an AI Engineering Knowledge Assistant.

Answer the user's question using ONLY the information
provided in the context below.

If the answer is not available in the context,
say that the information is not available in the uploaded document.

Context:
{context}

Question:
{question}

Answer:
"""


    # ===============================
    # Step 8: Ask Llama
    # ===============================

    response = llm.invoke(prompt)


    # ===============================
    # Step 9: Return answer
    # ===============================

    return {
        "question": question,
        "answer": response.content,
        "retrieved_chunks": results
    }