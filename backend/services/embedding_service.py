import hashlib
import re
import numpy as np

# Lightweight vector size
DIMENSION = 384


def create_embeddings(chunks):

    if len(chunks) == 0:
        return np.array([])

    embeddings = []

    for text in chunks:

        vector = np.zeros(DIMENSION, dtype="float32")

        # Convert text into simple words
        words = re.findall(r"\b\w+\b", text.lower())

        for word in words:

            # Convert word into a stable number
            hash_value = int(
                hashlib.md5(word.encode()).hexdigest(),
                16
            )

            index = hash_value % DIMENSION

            vector[index] += 1

        # Normalize vector
        norm = np.linalg.norm(vector)

        if norm > 0:
            vector = vector / norm

        embeddings.append(vector)

    embeddings = np.array(embeddings, dtype="float32")

    print("Embeddings Shape:", embeddings.shape)

    return embeddings