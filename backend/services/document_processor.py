from pathlib import Path
from typing import Any

import fitz
from docx import Document


DEFAULT_CHUNK_SIZE = 800
DEFAULT_CHUNK_OVERLAP = 100


def clean_text(text: str) -> str:
    return " ".join(text.split())


def create_chunks(
    text: str,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    chunk_overlap: int = DEFAULT_CHUNK_OVERLAP,
) -> list[str]:
    if not text:
        return []

    if chunk_overlap >= chunk_size:
        raise ValueError(
            "chunk_overlap must be smaller than chunk_size"
        )

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        if end >= len(text):
            break

        start = end - chunk_overlap

    return chunks


def process_pdf(file_path: Path) -> list[dict[str, Any]]:
    results = []

    document = fitz.open(file_path)

    try:
        for page_index, page in enumerate(document):
            text = clean_text(page.get_text())

            if not text:
                continue

            chunks = create_chunks(text)

            for chunk_index, chunk in enumerate(chunks):
                results.append(
                    {
                        "chunk_id": (
                            f"{file_path.stem}"
                            f"_p{page_index + 1}"
                            f"_c{chunk_index + 1}"
                        ),
                        "text": chunk,
                        "source_file": file_path.name,
                        "page": page_index + 1,
                    }
                )
    finally:
        document.close()

    return results


def process_docx(file_path: Path) -> list[dict[str, Any]]:
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        text = clean_text(paragraph.text)

        if text:
            paragraphs.append(text)

    full_text = " ".join(paragraphs)
    chunks = create_chunks(full_text)

    results = []

    for chunk_index, chunk in enumerate(chunks):
        results.append(
            {
                "chunk_id": (
                    f"{file_path.stem}"
                    f"_c{chunk_index + 1}"
                ),
                "text": chunk,
                "source_file": file_path.name,
                "page": None,
            }
        )

    return results


def process_txt(file_path: Path) -> list[dict[str, Any]]:
    text = file_path.read_text(
        encoding="utf-8",
        errors="ignore"
    )

    text = clean_text(text)
    chunks = create_chunks(text)

    results = []

    for chunk_index, chunk in enumerate(chunks):
        results.append(
            {
                "chunk_id": (
                    f"{file_path.stem}"
                    f"_c{chunk_index + 1}"
                ),
                "text": chunk,
                "source_file": file_path.name,
                "page": None,
            }
        )

    return results


def process_document(
    file_path: str,
) -> list[dict[str, Any]]:
    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(
            f"File not found: {file_path}"
        )

    extension = path.suffix.lower()

    if extension == ".pdf":
        return process_pdf(path)

    if extension == ".docx":
        return process_docx(path)

    if extension == ".txt":
        return process_txt(path)

    raise ValueError(
        f"Unsupported file type: {extension}. "
        "Only PDF, DOCX and TXT files are supported."
    )
