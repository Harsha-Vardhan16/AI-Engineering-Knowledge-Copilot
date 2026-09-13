import os
import faiss
import numpy as np


# ===============================
# Base directory
# ===============================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_DIR = os.path.join(BASE_DIR, "vector_store")
INDEX_PATH = os.path.join(INDEX_DIR, "faiss_index.bin")


index = None


# ===============================
# Initialize FAISS
# ===============================

def initialize_index(dimension):
    global index

    index = faiss.IndexFlatL2(dimension)


# ===============================
# Load FAISS index
# ===============================

def load_index():
    global index

    if os.path.exists(INDEX_PATH):

        index = faiss.read_index(INDEX_PATH)

        print("FAISS index loaded.")

    else:

        print("No FAISS index found at:", INDEX_PATH)


# ===============================
# Add embeddings
# ===============================

def add_embeddings(embeddings):
    global index

    embeddings = np.array(embeddings).astype("float32")

    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    print("Embeddings Shape:", embeddings.shape)

    if index is None:
        initialize_index(embeddings.shape[1])

    index.add(embeddings)


# ===============================
# Save FAISS index
# ===============================

def save_index():
    global index

    if index is not None:

        # Make sure the correct directory exists
        os.makedirs(INDEX_DIR, exist_ok=True)

        # Save using the same absolute path
        faiss.write_index(index, INDEX_PATH)

        print("FAISS index saved at:", INDEX_PATH)


# ===============================
# Search FAISS
# ===============================

def search(query_embedding, k=3):
    global index

    if index is None:
        load_index()

    if index is None:
        raise Exception(
            "No FAISS index found. Upload a PDF first."
        )

    query_embedding = np.array(query_embedding).astype("float32")

    if len(query_embedding.shape) == 1:
        query_embedding = query_embedding.reshape(1, -1)

    distances, indices = index.search(
        query_embedding,
        k
    )

    return indices