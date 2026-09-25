from pathlib import Path
import json

import faiss
import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer


class SearchService:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        self.index = None
        self.chunks = []
        self.bm25 = None

        self.index_dir = Path("data/index")
        self.index_dir.mkdir(parents=True, exist_ok=True)

        self.load_index()

    def rebuild_bm25(self):
        if not self.chunks:
            self.bm25 = None
            return

        tokenized_documents = [
            chunk["text"].lower().split()
            for chunk in self.chunks
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    def add_chunks(self, chunks):
        if not chunks:
            return

        embeddings = self.model.encode(
            [chunk["text"] for chunk in chunks],
            normalize_embeddings=True
        )

        embeddings = np.asarray(
            embeddings,
            dtype="float32"
        )

        if self.index is None:
            dimension = embeddings.shape[1]
            self.index = faiss.IndexFlatIP(dimension)

        self.index.add(embeddings)
        self.chunks.extend(chunks)

        self.rebuild_bm25()
        self.save_index()

    def search(self, query, top_k=5):
        if not self.chunks or self.index is None:
            return []

        query_embedding = self.model.encode(
            [query],
            normalize_embeddings=True
        )

        query_embedding = np.asarray(
            query_embedding,
            dtype="float32"
        )

        candidate_k = min(
            max(top_k * 3, 10),
            len(self.chunks)
        )

        semantic_scores, semantic_indices = self.index.search(
            query_embedding,
            candidate_k
        )

        semantic_scores = semantic_scores[0]
        semantic_indices = semantic_indices[0]

        keyword_scores = np.zeros(len(self.chunks))

        if self.bm25 is not None:
            keyword_scores = self.bm25.get_scores(
                query.lower().split()
            )

        candidates = []

        for position, chunk_index in enumerate(semantic_indices):
            if chunk_index < 0:
                continue

            semantic_score = float(
                semantic_scores[position]
            )

            keyword_score = float(
                keyword_scores[chunk_index]
            )

            candidates.append(
                {
                    "chunk_index": int(chunk_index),
                    "semantic_score": semantic_score,
                    "keyword_score": keyword_score
                }
            )

        if not candidates:
            return []

        semantic_values = np.array(
            [item["semantic_score"] for item in candidates]
        )

        keyword_values = np.array(
            [item["keyword_score"] for item in candidates]
        )

        def normalize(values):
            minimum = values.min()
            maximum = values.max()

            if maximum == minimum:
                return np.ones_like(values)

            return (values - minimum) / (
                maximum - minimum
            )

        semantic_normalized = normalize(
            semantic_values
        )

        keyword_normalized = normalize(
            keyword_values
        )

        for i, item in enumerate(candidates):
            item["score"] = (
                0.7 * semantic_normalized[i]
                + 0.3 * keyword_normalized[i]
            )

        candidates.sort(
            key=lambda item: item["score"],
            reverse=True
        )

        results = []

        for item in candidates[:top_k]:
            chunk = self.chunks[item["chunk_index"]]

            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text"],
                    "source_file": chunk["source_file"],
                    "page": chunk.get("page"),
                    "score": float(item["score"]),
                    "semantic_score": float(
                        item["semantic_score"]
                    ),
                    "keyword_score": float(
                        item["keyword_score"]
                    )
                }
            )

        return results

    def save_index(self):
        if self.index is not None:
            faiss.write_index(
                self.index,
                str(self.index_dir / "documents.faiss")
            )

        with open(
            self.index_dir / "chunks.json",
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.chunks,
                file,
                ensure_ascii=False,
                indent=2
            )

    def load_index(self):
        index_path = self.index_dir / "documents.faiss"
        chunks_path = self.index_dir / "chunks.json"

        if index_path.exists() and chunks_path.exists():
            self.index = faiss.read_index(
                str(index_path)
            )

            with open(
                chunks_path,
                "r",
                encoding="utf-8"
            ) as file:
                self.chunks = json.load(file)

            self.rebuild_bm25()
