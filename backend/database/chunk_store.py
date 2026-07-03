import pickle
import os

CHUNK_FILE = "database/chunks.pkl"


def save_chunks(chunks):
    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)


def load_chunks():
    if not os.path.exists(CHUNK_FILE):
        return []

    with open(CHUNK_FILE, "rb") as f:
        return pickle.load(f)