from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.upload import search_service
from services.chat_service import OllamaChatService

router = APIRouter(prefix="/chat", tags=["Chat"])

ollama_service = OllamaChatService()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    mode: Literal["auto", "documents", "general"] = "auto"
    top_k: int = Field(default=5, ge=1, le=10)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatSource(BaseModel):
    chunk_id: str
    source_file: str
    page: int | None = None
    score: float
    semantic_score: float
    keyword_score: float
    text: str


class ChatResponse(BaseModel):
    answer: str
    mode: str
    sources: list[ChatSource]


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    question = request.message.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty."
        )

    history = [
        {
            "role": message.role,
            "content": message.content
        }
        for message in request.history[-10:]
    ]

    try:
        # ---------------------------------------------------------
        # EXPLICIT GENERAL MODE
        # ---------------------------------------------------------
        if request.mode == "general":
            answer = ollama_service.answer_general(
                question=question,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="general",
                sources=[]
            )

        # ---------------------------------------------------------
        # SEARCH UPLOADED DOCUMENTS
        # ---------------------------------------------------------
        results = search_service.search(
            query=question,
            top_k=request.top_k
        )

        # ---------------------------------------------------------
        # EXPLICIT DOCUMENT MODE
        # ---------------------------------------------------------
        if request.mode == "documents":
            if not results:
                return ChatResponse(
                    answer=(
                        "I could not find relevant information "
                        "in the uploaded documents."
                    ),
                    mode="documents",
                    sources=[]
                )

            answer = ollama_service.answer_from_documents(
                question=question,
                search_results=results,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="documents",
                sources=[
                    ChatSource(**result)
                    for result in results
                ]
            )

        # ---------------------------------------------------------
        # AUTO MODE
        #
        # ContextIQ decides whether the user is asking about the
        # uploaded documents or asking a general knowledge question.
        # ---------------------------------------------------------

        question_lower = question.lower()

        # Words/phrases that explicitly connect the question
        # to an uploaded document or a person described in it.
        document_terms = (
            "resume",
            "cv",
            "curriculum vitae",
            "uploaded document",
            "uploaded file",
            "this document",
            "the document",
            "this file",
            "the file",
            "according to the document",
            "according to the resume",
            "according to the cv",
            "in the resume",
            "in the cv",
            "in the document",
            "from the resume",
            "from the cv",
            "from the document",
            "listed in",
            "mentioned in",
            "mentioned on",
            "according to",
            "what does she",
            "what does he",
            "what are her",
            "what are his",
            "what is her",
            "what is his",
            "her experience",
            "his experience",
            "her skills",
            "his skills",
            "her education",
            "his education",
            "her projects",
            "his projects",
            "her certifications",
            "his certifications",
            "her background",
            "his background",
        )

        asks_about_document = any(
            term in question_lower
            for term in document_terms
        )

        # Questions beginning with these phrases are normally
        # general knowledge questions unless they explicitly
        # refer to the uploaded document.
        generic_question_starts = (
            "what is ",
            "what are ",
            "who is ",
            "who are ",
            "why is ",
            "why are ",
            "how does ",
            "how do ",
            "explain ",
            "define ",
            "tell me about ",
        )

        is_generic_question = question_lower.startswith(
            generic_question_starts
        )

        # ---------------------------------------------------------
        # DOCUMENT QUESTION
        # ---------------------------------------------------------
        #
        # Example:
        # "What skills are listed in the resume?"
        # "What are her projects?"
        # "What certifications are mentioned in the CV?"
        #
        if results and asks_about_document:
            answer = ollama_service.answer_from_documents(
                question=question,
                search_results=results,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="documents",
                sources=[
                    ChatSource(**result)
                    for result in results
                ]
            )

        # ---------------------------------------------------------
        # GENERAL QUESTION
        # ---------------------------------------------------------
        #
        # Example:
        # "What is AI?"
        # "What is machine learning?"
        # "Explain cloud computing."
        #
        # Even if an uploaded document happens to mention AI,
        # these questions should normally be answered generally.
        #
        if is_generic_question and not asks_about_document:
            answer = ollama_service.answer_general(
                question=question,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="general",
                sources=[]
            )

        # ---------------------------------------------------------
        # OTHER QUESTIONS
        # ---------------------------------------------------------
        #
        # If the question does not clearly look like a generic
        # knowledge question and relevant document results exist,
        # use the document context.
        #
        # This supports natural questions such as:
        # "Where did she study?"
        # "Does she know Python?"
        # "Tell me about her experience."
        #
        if results:
            answer = ollama_service.answer_from_documents(
                question=question,
                search_results=results,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="documents",
                sources=[
                    ChatSource(**result)
                    for result in results
                ]
            )

        # ---------------------------------------------------------
        # NO DOCUMENT RESULTS
        # ---------------------------------------------------------
        #
        # Nothing relevant was found in uploaded documents,
        # so answer using the local Ollama model.
        #
        answer = ollama_service.answer_general(
            question=question,
            history=history
        )

        return ChatResponse(
            answer=answer,
            mode="general",
            sources=[]
        )

    except RuntimeError as error:
        raise HTTPException(
            status_code=503,
            detail=str(error)
        ) from error

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Chat processing failed: {error}"
        ) from error