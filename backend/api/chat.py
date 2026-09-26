from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from api.upload import search_service
from services.chat_service import OllamaChatService


router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)


ollama_service = OllamaChatService()


class ChatMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    message: str = Field(
        min_length=1,
        max_length=4000
    )

    mode: Literal[
        "auto",
        "documents",
        "general"
    ] = "auto"

    top_k: int = Field(
        default=5,
        ge=1,
        le=10
    )

    history: list[ChatMessage] = Field(
        default_factory=list
    )


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
        # --------------------------------------------------------
        # GENERAL MODE
        # --------------------------------------------------------
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

        # --------------------------------------------------------
        # DOCUMENT SEARCH
        # --------------------------------------------------------
        results = search_service.search(
            query=question,
            top_k=request.top_k
        )

        # --------------------------------------------------------
        # DOCUMENT MODE
        # --------------------------------------------------------
        if request.mode == "documents":
            if not results:
                return ChatResponse(
                    answer=(
                        "I could not find relevant content in "
                        "the uploaded documents."
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

        # --------------------------------------------------------
        # AUTO MODE
        #
        # Use document context when the search system finds a
        # meaningful semantic or keyword match.
        # --------------------------------------------------------
        document_results = [
            result
            for result in results
            if (
                result.get("semantic_score", 0.0) >= 0.35
                or result.get("keyword_score", 0.0) > 0.0
            )
        ]

        if document_results:
            answer = ollama_service.answer_from_documents(
                question=question,
                search_results=document_results,
                history=history
            )

            return ChatResponse(
                answer=answer,
                mode="documents",
                sources=[
                    ChatSource(**result)
                    for result in document_results
                ]
            )

        # --------------------------------------------------------
        # FALL BACK TO GENERAL LOCAL AI
        # --------------------------------------------------------
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
