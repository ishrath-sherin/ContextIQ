import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatIP(dimension)

    def add(self, embeddings):
        vectors = np.asarray(embeddings, dtype="float32")
        self.index.add(vectors)

    def search(self, query_embedding, top_k: int = 5):
        query = np.asarray(query_embedding, dtype="float32")
        scores, indices = self.index.search(query, top_k)

        return scores, indices
    