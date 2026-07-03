from fastapi import APIRouter, UploadFile, File
from services.pdf_loader import extract_text_from_pdf
from rag.text_chunker import create_chunks
from services.embedding_service import create_embeddings
from vector_store.faiss_store import add_embeddings, save_index
from database.chunk_store import save_chunks

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"uploads/{file.filename}"

    # Save uploaded PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text from PDF
    text = extract_text_from_pdf(file_path)

    # Create chunks
    chunks = create_chunks(text)

    # Save chunks
    save_chunks(chunks)

    # Create embeddings
    embeddings = create_embeddings(chunks)

    # Store embeddings in FAISS
    add_embeddings(embeddings)

    # Save FAISS index
    save_index()

    return {
        "message": "PDF uploaded and stored successfully",
        "chunks": len(chunks)
    }
text = extract_text_from_pdf(file_path)

print("TEXT LENGTH:", len(text))
print(text[:500])
chunks = create_chunks(text)

print("CHUNKS:", len(chunks))