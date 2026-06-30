from fastapi import APIRouter, UploadFile, File
import shutil
import os

from services.pdf_loader import extract_text_from_pdf
from rag.text_chunker import create_chunks

router = APIRouter()

UPLOAD_DIR = "uploads"

@router.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    text = extract_text_from_pdf(file_path)
    chunks = create_chunks(text)

    return {
        "filename": file.filename,
        "total_characters": len(text),
        "total_chunks": len(chunks),
        "first_chunk": chunks[0] if chunks else ""
    }