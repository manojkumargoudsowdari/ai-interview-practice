import re
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from fastapi import UploadFile
from pypdf import PdfReader


BACKEND_DIR = Path(__file__).resolve().parents[2]
UPLOAD_DIR = BACKEND_DIR / "data" / "uploads"
SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


class DocumentProcessingError(ValueError):
    pass


@dataclass
class ProcessedDocument:
    filename: str
    saved_path: Path
    text: str
    character_count: int
    preview: str


def clean_text(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def make_preview(text: str, max_length: int = 240) -> str:
    if len(text) <= max_length:
        return text
    return f"{text[:max_length].rstrip()}..."


async def process_uploaded_file(file: UploadFile) -> ProcessedDocument:
    filename = Path(file.filename or "").name
    extension = Path(filename).suffix.lower()

    if not filename:
        raise DocumentProcessingError("Uploaded file must have a filename.")

    if extension not in SUPPORTED_EXTENSIONS:
        supported = ", ".join(sorted(SUPPORTED_EXTENSIONS))
        raise DocumentProcessingError(f"Unsupported file type '{extension}'. Supported types: {supported}.")

    content = await file.read()
    if not content:
        raise DocumentProcessingError("Uploaded file is empty.")

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    saved_path = UPLOAD_DIR / filename
    saved_path.write_bytes(content)

    if extension in {".txt", ".md"}:
        text = _decode_text(content)
    else:
        text = _extract_pdf_text(content, filename)

    cleaned = clean_text(text)
    if not cleaned:
        raise DocumentProcessingError("No readable text could be extracted from the uploaded file.")

    return ProcessedDocument(
        filename=filename,
        saved_path=saved_path,
        text=cleaned,
        character_count=len(cleaned),
        preview=make_preview(cleaned),
    )


def process_text_payload(text: str, source: str = "pasted_text") -> ProcessedDocument:
    cleaned = clean_text(text)
    if not cleaned:
        raise DocumentProcessingError("Text payload is empty.")

    return ProcessedDocument(
        filename=source,
        saved_path=Path(source),
        text=cleaned,
        character_count=len(cleaned),
        preview=make_preview(cleaned),
    )


def _decode_text(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="replace")


def _extract_pdf_text(content: bytes, filename: str) -> str:
    try:
        reader = PdfReader(BytesIO(content))
        return "\n".join(page.extract_text() or "" for page in reader.pages)
    except Exception as exc:
        raise DocumentProcessingError(f"Could not extract text from PDF '{filename}'.") from exc
