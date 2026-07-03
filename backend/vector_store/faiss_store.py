import faiss
import numpy as np

index = None

def initialize_index(dimension):
    global index
    index = faiss.IndexFlatL2(dimension)


def add_embeddings(embeddings):
    global index

    embeddings = np.array(embeddings).astype("float32")

    if len(embeddings.shape) == 1:
        embeddings = embeddings.reshape(1, -1)

    print("Embedding Shape:", embeddings.shape)

    if index is None:
        initialize_index(embeddings.shape[1])

    index.add(embeddings)


def save_index():
    global index
    faiss.write_index(index, "vector_store/faiss_index.bin")


def search(query_embedding, k=3):
    global index
    distances, indices = index.search(query_embedding, k)
    return indices