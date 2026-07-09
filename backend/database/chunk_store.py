import pickle
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHUNK_FILE = os.path.join(BASE_DIR, "database", "chunks.pkl")


def save_chunks(chunks):
    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)


def load_chunks():
    if not os.path.exists(CHUNK_FILE):
        return []

    with open(CHUNK_FILE, "rb") as f:
        return pickle.load(f)