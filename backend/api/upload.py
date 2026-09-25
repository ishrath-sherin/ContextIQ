from pathlib import Path
import shutil
import uuid

from fastapi import APIRouter, File, HTTPException, UploadFile

from models.schemas import Chunk, UploadResponse
from services.document_processor import process_document
from services.search.search_service import SearchService


router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)

UPLOAD_DIR = Path("data/uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

search_service = SearchService()


@router.post("", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...)
):
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required."
        )

    extension = Path(file.filename).suffix.lower()

    allowed_extensions = {".pdf", ".docx", ".txt"}

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX and TXT files are supported."
        )

    unique_filename = f"{uuid.uuid4().hex}{extension}"
    file_path = UPLOAD_DIR / unique_filename

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        chunks = process_document(str(file_path))

        if not chunks:
            raise HTTPException(
                status_code=400,
                detail="No readable text found in the document."
            )

        search_service.add_chunks(chunks)

        return UploadResponse(
            filename=file.filename,
            status="processed",
            chunk_count=len(chunks),
            chunks=[
                Chunk(**chunk)
                for chunk in chunks
            ]
        )

    except HTTPException:
        raise

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Document processing failed: {error}"
        )