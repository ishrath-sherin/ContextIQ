from sentence_transformers import SentenceTransformer

from services.search.vector_store import VectorStore
from services.search.keyword_search import KeywordSearch


class SearchService:
    def __init__(self, documents):
        self.documents = documents

        self.embedding_model = SentenceTransformer(
            "all-MiniLM-L6-v2"
        )

        embeddings = self.embedding_model.encode(
            documents,
            normalize_embeddings=True
        )

        self.vector_store = VectorStore(
            dimension=embeddings.shape[1]
        )

        self.vector_store.add(embeddings)

        self.keyword_search = KeywordSearch(
            documents
        )

    def search(self, query, top_k=5):
        if not self.documents:
            return []

        # Create embedding for the user's query
        query_embedding = self.embedding_model.encode(
            [query],
            normalize_embeddings=True
        )

        # Retrieve semantic scores for all documents
        semantic_scores, semantic_indices = (
            self.vector_store.search(
                query_embedding,
                len(self.documents)
            )
        )

        semantic_scores = semantic_scores[0]
        semantic_indices = semantic_indices[0]

        # Normalize semantic scores
        min_semantic = float(min(semantic_scores))
        max_semantic = float(max(semantic_scores))

        if max_semantic > min_semantic:
            normalized_semantic = {
                int(index): float(
                    (score - min_semantic)
                    / (max_semantic - min_semantic)
                )
                for score, index in zip(
                    semantic_scores,
                    semantic_indices
                )
            }
        else:
            normalized_semantic = {
                int(index): 0.0
                for index in semantic_indices
            }

        # Retrieve BM25 scores
        keyword_results = self.keyword_search.search(
            query,
            len(self.documents)
        )

        bm25_scores = [
            score
            for _, _, score in keyword_results
        ]

        min_bm25 = min(bm25_scores)
        max_bm25 = max(bm25_scores)

        normalized_bm25 = {}

        if max_bm25 > min_bm25:
            for document_index, _, score in keyword_results:
                normalized_bm25[document_index] = (
                    (score - min_bm25)
                    / (max_bm25 - min_bm25)
                )
        else:
            # No meaningful BM25 difference.
            # If all scores are zero, there is no keyword signal.
            for document_index, _, _ in keyword_results:
                normalized_bm25[document_index] = 0.0

        # Hybrid ranking
        hybrid_results = []

        for index, document in enumerate(self.documents):

            semantic_score = normalized_semantic.get(
                index,
                0.0
            )

            keyword_score = normalized_bm25.get(
                index,
                0.0
            )

            hybrid_score = (
                0.7 * semantic_score
                + 0.3 * keyword_score
            )

            hybrid_results.append(
                {
                    "document": document,
                    "semantic_score": float(
                        semantic_score
                    ),
                    "keyword_score": float(
                        keyword_score
                    ),
                    "hybrid_score": float(
                        hybrid_score
                    )
                }
            )

        hybrid_results.sort(
            key=lambda result: result["hybrid_score"],
            reverse=True
        )

        return hybrid_results[:top_k]