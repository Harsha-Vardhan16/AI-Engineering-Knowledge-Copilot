from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def create_embeddings(chunks):

    if len(chunks) == 0:
        return np.array([])

    embeddings = model.encode(chunks)

    print("Embeddings Shape:", embeddings.shape)

    return embeddings