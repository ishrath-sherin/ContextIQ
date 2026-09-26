from pathlib import Path

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.decomposition import PCA


class MeaningRadarService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def build_radar(self, chunks, query=None, limit=100):
        if not chunks:
            return {
                "query": query,
                "points": []
            }

        selected_chunks = chunks[:limit]

        texts = [
            chunk["text"]
            for chunk in selected_chunks
        ]

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        labels = [
            "document"
            for _ in selected_chunks
        ]

        if query and query.strip():
            query_embedding = self.model.encode(
                [query],
                normalize_embeddings=True
            )

            query_embedding = np.asarray(
                query_embedding,
                dtype="float32"
            )

            embeddings = np.vstack(
                [embeddings, query_embedding]
            )

            labels.append("query")

        if len(embeddings) == 1:
            coordinates = np.array(
                [[0.0, 0.0]],
                dtype="float32"
            )
        elif len(embeddings) == 2:
            coordinates = np.array(
                [
                    [-1.0, 0.0],
                    [1.0, 0.0]
                ],
                dtype="float32"
            )
        else:
            pca = PCA(n_components=2)
            coordinates = pca.fit_transform(
                embeddings
            )

        points = []

        for index, (x, y) in enumerate(coordinates):
            if index < len(selected_chunks):
                chunk = selected_chunks[index]

                points.append(
                    {
                        "id": chunk["chunk_id"],
                        "type": "document",
                        "x": float(x),
                        "y": float(y),
                        "source_file": chunk["source_file"],
                        "page": chunk.get("page"),
                        "text": chunk["text"]
                    }
                )
            else:
                points.append(
                    {
                        "id": "query",
                        "type": "query",
                        "x": float(x),
                        "y": float(y),
                        "source_file": None,
                        "page": None,
                        "text": query
                    }
                )

        return {
            "query": query,
            "points": points
        }
