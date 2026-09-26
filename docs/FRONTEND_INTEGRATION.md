# ContextIQ Frontend Integration Guide

## Backend URL

Development backend:

http://127.0.0.1:8000

Swagger API documentation:

http://127.0.0.1:8000/docs

---

## 1. Health Check

GET:

/health

Example response:

{
    "status": "healthy"
}

---

## 2. Upload Documents

POST:

/upload

The frontend should send uploaded PDF, DOCX, or TXT files as multipart/form-data.

The backend extracts the text, creates chunks, generates embeddings, and
updates the search index.

---

## 3. Search

POST:

/search

Request:

{
    "query": "What is semantic search?",
    "top_k": 5
}

Response structure:

{
    "query": "What is semantic search?",
    "results": [
        {
            "chunk_id": "...",
            "text": "...",
            "source_file": "...",
            "page": null,
            "score": 0.95,
            "semantic_score": 0.55,
            "keyword_score": 5.29
        }
    ]
}

The frontend can display:

- retrieved text
- source filename
- page number when available
- hybrid score
- semantic score
- keyword score

---

## 4. Chatbot

POST:

/chat

### General question

Request:

{
    "message": "What is artificial intelligence?",
    "mode": "general",
    "top_k": 3,
    "history": []
}

### Document-grounded question

Request:

{
    "message": "What is FAISS used for in ContextIQ?",
    "mode": "documents",
    "top_k": 3,
    "history": []
}

Response structure:

{
    "answer": "...",
    "mode": "documents",
    "sources": [
        {
            "chunk_id": "...",
            "source_file": "...",
            "page": null,
            "score": 1.0,
            "semantic_score": 0.54,
            "keyword_score": 10.94,
            "text": "..."
        }
    ]
}

For general questions, sources may be an empty array.

---

## 5. Meaning Radar

GET:

/meaning-radar

Optional query:

/meaning-radar?query=semantic%20search&limit=10

Response:

{
    "query": "semantic search",
    "points": [
        {
            "id": "...",
            "type": "document",
            "x": 0.12,
            "y": -0.35,
            "source_file": "...",
            "page": null,
            "text": "..."
        },
        {
            "id": "query",
            "type": "query",
            "x": 0.42,
            "y": 0.18,
            "source_file": null,
            "page": null,
            "text": "semantic search"
        }
    ]
}

The frontend can plot:

type = "document"
    → document point

type = "query"
    → query point

The x/y values are PCA coordinates.

---

## 6. Recommended Frontend Flow

### Search screen

User enters query
        ↓
POST /search
        ↓
Display results
        ↓
Show source + page + scores

### Chat screen

User sends question
        ↓
POST /chat
        ↓
Display answer
        ↓
Display supporting sources when available

### Meaning Radar

User enters optional query
        ↓
GET /meaning-radar?query=...
        ↓
Plot returned x/y coordinates

### Upload

User selects PDF/DOCX/TXT
        ↓
POST /upload
        ↓
Show upload/indexing status
        ↓
Allow search against uploaded content

---

## 7. CORS

The backend currently allows frontend development requests through CORS.

The frontend can therefore communicate with:

http://127.0.0.1:8000

during local development.

---

## 8. Important Frontend Notes

Do not hard-code individual document filenames.

Use the source_file field returned by the API.

Do not assume page is always available.

For TXT and DOCX documents, page may be null.

For search results, use the returned score fields rather than calculating
scores again in React.

For Meaning Radar, use the returned x and y values directly.

The backend owns search, ranking, embeddings, and chatbot logic.

The frontend should focus on presentation, interaction, visualization,
loading states, and error handling.
