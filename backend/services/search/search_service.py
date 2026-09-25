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

        # Retrieve enough semantic candidates for hybrid ranking.
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

        # Calculate BM25 scores for every chunk.
        keyword_scores = np.zeros(
            len(self.chunks),
            dtype="float32"
        )

        if self.bm25 is not None:
            keyword_scores = np.asarray(
                self.bm25.get_scores(
                    query.lower().split()
                ),
                dtype="float32"
            )

        # Use the union of semantic candidates and keyword candidates.
        semantic_candidates = {
            int(index)
            for index in semantic_indices
            if index >= 0
        }

        keyword_candidate_count = min(
            max(top_k * 3, 10),
            len(self.chunks)
        )

        keyword_indices = np.argsort(
            keyword_scores
        )[::-1][:keyword_candidate_count]

        candidate_indices = (
            semantic_candidates
            | {
                int(index)
                for index in keyword_indices
            }
        )

        if not candidate_indices:
            return []

        # Build score lookup for semantic results.
        semantic_score_map = {
            int(index): float(score)
            for score, index in zip(
                semantic_scores,
                semantic_indices
            )
            if index >= 0
        }

        candidates = []

        for chunk_index in candidate_indices:
            candidates.append(
                {
                    "chunk_index": chunk_index,
                    "semantic_score": semantic_score_map.get(
                        chunk_index,
                        0.0
                    ),
                    "keyword_score": float(
                        keyword_scores[chunk_index]
                    )
                }
            )

        semantic_values = np.array(
            [
                item["semantic_score"]
                for item in candidates
            ],
            dtype="float32"
        )

        keyword_values = np.array(
            [
                item["keyword_score"]
                for item in candidates
            ],
            dtype="float32"
        )

        def normalize(values):
            minimum = values.min()
            maximum = values.max()

            if maximum > minimum:
                return (
                    (values - minimum)
                    / (maximum - minimum)
                )

            # No useful variation in this signal.
            return np.zeros_like(values)

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