import os
import faiss
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX_PATH = os.path.join(BASE_DIR, "vector_store", "faiss_index.bin")

index = None


def initialize_index(dimension):
    global index
    index = faiss.IndexFlatL2(dimension)


def load_index():
    global index

    if os.path.exists(INDEX_PATH):
        index = faiss.read_index(INDEX_PATH)
        print("FAISS index loaded.")
    else:
        print("No FAISS index found.")


def add_embeddings(embeddings):
    global index

    embeddings = np.array(embeddings).astype("float32")

    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    print("Embeddings Shape:", embeddings.shape)

    if index is None:
        initialize_index(embeddings.shape[1])

    index.add(embeddings)


def save_index():
    global index

    if index is not None:
        os.makedirs("vector_store", exist_ok=True)
        faiss.write_index(index, INDEX_PATH)
        print("FAISS index saved.")


def search(query_embedding, k=3):
    global index

    if index is None:
        load_index()

    if index is None:
        raise Exception("No FAISS index found. Upload a PDF first.")

    query_embedding = np.array(query_embedding).astype("float32")

    if len(query_embedding.shape) == 1:
        query_embedding = query_embedding.reshape(1, -1)

    distances, indices = index.search(query_embedding, k)

    return indices