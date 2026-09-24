from services.search.embedding_service import EmbeddingService
from services.search.vector_store import VectorStore
from services.search.keyword_search import KeywordSearch


class SearchService:
    def __init__(self, documents):
        self.documents = documents

        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(384)
        self.keyword_search = KeywordSearch(documents)

        embeddings = self.embedding_service.encode(documents)
        self.vector_store.add(embeddings)

    def search(self, query, top_k=5):
        query_embedding = self.embedding_service.encode([query])

        semantic_scores, semantic_indices = self.vector_store.search(
            query_embedding,
            top_k
        )

        keyword_results = self.keyword_search.search(query, top_k)

        return {
            "semantic_results": [
                {
                    "document": self.documents[index],
                    "score": float(score)
                }
                for score, index in zip(
                    semantic_scores[0],
                    semantic_indices[0]
                )
            ],
            "keyword_results": [
                {
                    "document": document,
                    "score": float(score)
                }
                for document, score in keyword_results
            ]
        }