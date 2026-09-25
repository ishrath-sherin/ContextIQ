from rank_bm25 import BM25Okapi


class KeywordSearch:
    def __init__(self, documents):
        self.documents = documents

        tokenized_documents = [
            doc.lower().split()
            for doc in documents
        ]

        self.bm25 = BM25Okapi(tokenized_documents)

    def search(self, query, top_k=5):
        tokenized_query = query.lower().split()

        scores = self.bm25.get_scores(tokenized_query)

        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        return [
            (i, self.documents[i], float(scores[i]))
            for i in ranked_indices
        ]