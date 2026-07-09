from fastapi import APIRouter, UploadFile, File
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")

router = APIRouter()


@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    from services.pdf_loader import extract_text_from_pdf
    from rag.text_chunker import create_chunks
    from services.embedding_service import create_embeddings
    from vector_store.faiss_store import add_embeddings, save_index
    from database.chunk_store import save_chunks

    text = extract_text_from_pdf(file_path)

    if not text.strip():
        return {
            "success": False,
            "message": "No text found in PDF."
        }

    chunks = create_chunks(text)

    save_chunks(chunks)

    embeddings = create_embeddings(chunks)

    add_embeddings(embeddings)

    save_index()
    return {
    "success": True,
    "filename": file.filename,
    "chunks": len(chunks),
    "total_characters": len(text),
    "message": "PDF uploaded successfully"
}

    