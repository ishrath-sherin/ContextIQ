# ContextIQ — ML and Search Architecture

## 1. Overview

ContextIQ is a privacy-focused semantic search engine that combines semantic
search, keyword search, hybrid ranking, document metadata, and local AI
question answering.

The ML/search pipeline is:

Document
    ↓
Text Extraction
    ↓
Chunking
    ↓
Sentence Transformer Embeddings
    ↓
 ┌───────────────┬───────────────┐
 │               │               │
FAISS           BM25
 │               │
Semantic        Keyword
Search          Search
 │               │
 └───────┬───────┘
         ↓
   Hybrid Ranking
         ↓
   Relevant Results
         ↓
 Local LLM / Ollama
         ↓
 Grounded Answer

---

## 2. Document Processing

ContextIQ accepts PDF, DOCX, and TXT documents.

The backend extracts the document text and divides it into smaller chunks.
Each chunk retains metadata such as:

- chunk ID
- source filename
- page number when available
- chunk text

Chunking allows the search system to retrieve specific passages instead of
returning an entire document.

---

## 3. Sentence Transformer Embeddings

ContextIQ uses the Sentence Transformers model:

    all-MiniLM-L6-v2

Each document chunk is converted into a numerical vector called an embedding.

The embedding represents the semantic meaning of the text.

This allows ContextIQ to retrieve passages that are conceptually similar to
a user's query even when they do not contain exactly the same words.

For example:

Query:
    "How does ContextIQ find documents by meaning?"

A relevant document containing:
    "ContextIQ uses semantic search to find documents by meaning."

can be retrieved through semantic similarity.

Embeddings are normalized before being stored and searched.

---

## 4. FAISS Vector Search

FAISS is used for efficient vector similarity search.

ContextIQ uses:

    IndexFlatIP

The embedding vectors are normalized, so inner-product similarity can be used
as the semantic similarity measure.

During a search:

1. The query is converted into an embedding.
2. FAISS compares the query embedding with stored document embeddings.
3. The closest vectors are retrieved.
4. Their corresponding document chunks are returned as semantic candidates.

FAISS therefore provides the semantic-search component of ContextIQ.

---

## 5. BM25 Keyword Search

ContextIQ also uses BM25 for traditional keyword-based retrieval.

BM25 compares the words in the user's query with words appearing in the
indexed document chunks.

This is useful when exact terminology matters.

For example, a query containing:

    "FAISS vector similarity"

can strongly match a document containing those exact technical terms.

BM25 therefore provides the keyword-search component.

---

## 6. Hybrid Search

ContextIQ combines semantic search and keyword search.

The current hybrid ranking uses:

    Hybrid Score =
        0.7 × normalized semantic score
        +
        0.3 × normalized keyword score

Semantic similarity therefore contributes 70% of the hybrid score, while
keyword relevance contributes 30%.

This combination provides a balance between:

- meaning-based retrieval
- exact keyword matching

The system first collects candidates from both FAISS and BM25, then combines
their normalized scores before ranking the final results.

---

## 7. Score Explainability

Search results expose multiple scores instead of returning only one final
number.

Each result can include:

- hybrid score
- semantic score
- keyword score
- source filename
- page number
- chunk ID
- retrieved text

This makes the search process easier to inspect and explain during testing
and demonstration.

---

## 8. Relevance Threshold

A relevance threshold was added to reduce clearly unrelated search results.

Before hybrid ranking, the highest semantic similarity score is checked.

If the strongest semantic match is below:

    0.20

the search returns no results.

This prevents weakly related queries from being forced into the result list
only because of relative score normalization.

For example, an unrelated cooking query should not return an arbitrary
technical document simply because it happens to be the highest-scoring item
among otherwise poor matches.

---

## 9. Persistent Search Index

The search index is persisted under:

    backend/data/index/

Important files include:

    documents.faiss
    chunks.json

The FAISS index stores the vector representation used for semantic search.

The chunks JSON file stores the document chunks and their metadata.

The BM25 index is rebuilt from the stored chunks when the backend loads the
persistent index.

This allows the search system to retain its indexed documents across backend
restarts.

---

## 10. Meaning Radar

ContextIQ includes a Meaning Radar visualization.

The Meaning Radar converts document embeddings into two-dimensional
coordinates using Principal Component Analysis (PCA).

The visualization represents:

- document chunks as points
- an optional search query as a separate point

The original embeddings exist in a high-dimensional vector space.

PCA projects those vectors into two dimensions so that their relative
structure can be visualized.

The visualization is therefore intended as an explanatory representation of
semantic relationships rather than a replacement for the actual search
algorithm.

---

## 11. Local AI Chatbot

ContextIQ uses Ollama to run a local language model.

The current model is:

    llama3.2:3b

The chatbot supports two major modes.

### General mode

The model answers general questions without document context.

Example:

    What is artificial intelligence?

The response does not require a document search and returns no document
sources.

### Document mode

The system first searches the uploaded documents.

The retrieved passages are supplied to the local language model as context.

The model is instructed to:

- answer using the supplied document context
- avoid inventing unsupported information
- indicate when the supplied context is insufficient
- distinguish general knowledge from document-supported information
- use source/page information when useful

This creates a document-grounded question-answering pipeline.

---

## 12. Chatbot Grounding Validation

The chatbot was tested using document-based and general questions.

### Test 1 — ContextIQ technologies

Question:

    What technologies does ContextIQ use for semantic search and
    keyword-based ranking?

The system correctly identified:

- Sentence Transformers for semantic-search embeddings
- BM25 for keyword-based ranking

The response also returned supporting document sources.

### Test 2 — FAISS

Question:

    What is FAISS used for in ContextIQ?

The system correctly identified FAISS as the component used for vector
similarity search.

Supporting document sources were returned.

### Test 3 — Unsupported document question

A question unrelated to the uploaded documents was tested in document mode.

The system returned:

    I could not find relevant content in the uploaded documents.

No document sources were returned.

This demonstrates the intended behavior when the available document context
does not support an answer.

### Test 4 — General question

Question:

    What is artificial intelligence?

The system generated a general answer using the local LLM.

The response mode was:

    general

and the returned source list was empty.

This confirms that general questions can be answered independently of the
uploaded-document search pipeline.

---

## 13. Privacy-Focused Design

ContextIQ is designed around local processing.

The project uses:

- local document processing
- local embeddings
- local FAISS indexing
- local BM25 search
- local Ollama inference

The chatbot does not require an external AI API for the implemented
question-answering pipeline.

Project documentation should describe this as a privacy-focused or local
processing architecture rather than claiming absolute privacy or security.

---

## 14. ML/Search Components

| Component | Technology | Purpose |
|---|---|---|
| Embeddings | Sentence Transformers | Convert text into semantic vectors |
| Embedding model | all-MiniLM-L6-v2 | Generate document/query embeddings |
| Vector search | FAISS | Semantic similarity retrieval |
| Keyword search | BM25 | Exact keyword-based retrieval |
| Ranking | Hybrid 70/30 | Combine semantic and keyword relevance |
| Threshold | 0.20 semantic score | Reject clearly weak semantic matches |
| Visualization | PCA | Project embeddings into 2D |
| Local LLM | Ollama + llama3.2:3b | General and grounded answers |
| Persistence | FAISS + JSON | Preserve indexed documents |

---

## 15. End-to-End ML Pipeline

The complete ContextIQ ML/search workflow is:

1. User uploads a document.
2. Backend extracts the document text.
3. Text is divided into chunks.
4. Each chunk receives metadata.
5. Sentence Transformers generates embeddings.
6. Embeddings are normalized.
7. FAISS stores the vectors.
8. BM25 indexes the chunk text.
9. User submits a search query.
10. The query is converted into an embedding.
11. FAISS retrieves semantic candidates.
12. BM25 retrieves keyword candidates.
13. Candidate results are combined.
14. Semantic and keyword scores are normalized.
15. Hybrid scores are calculated using the 70/30 weighting.
16. The relevance threshold removes clearly weak queries.
17. Results are ranked.
18. Source metadata and scores are returned.
19. For document chat, retrieved passages are passed to the local LLM.
20. The local LLM generates a grounded response.

---

## 16. Key Contribution

The main ML contribution of ContextIQ is the combination of semantic and
keyword retrieval in a single search pipeline.

Semantic retrieval helps understand meaning.

BM25 helps preserve exact keyword relevance.

Hybrid ranking combines both signals.

The local LLM then extends the search system into a question-answering
interface using retrieved document context.

Meaning Radar provides an additional visual explanation of the semantic
embedding space.
