import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.schemas import PracticeContextResponse
from app.services.document_processor import make_preview


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
CONTEXT_PATH = PROCESSED_DIR / "context.json"

EMPTY_CONTEXT: dict[str, str | None] = {
    "resume_text": "",
    "job_description_text": "",
    "resume_filename": None,
    "job_description_filename": None,
    "updated_at": None,
}


def load_context() -> dict[str, Any]:
    if not CONTEXT_PATH.exists():
        return EMPTY_CONTEXT.copy()

    try:
        with CONTEXT_PATH.open("r", encoding="utf-8") as context_file:
            loaded = json.load(context_file)
    except (json.JSONDecodeError, OSError):
        return EMPTY_CONTEXT.copy()

    context = EMPTY_CONTEXT.copy()
    context.update(loaded)
    return context


def get_context_response() -> PracticeContextResponse:
    context = load_context()
    resume_text = context.get("resume_text") or ""
    job_description_text = context.get("job_description_text") or ""

    return PracticeContextResponse(
        has_resume=bool(resume_text),
        has_job_description=bool(job_description_text),
        resume_filename=context.get("resume_filename"),
        job_description_filename=context.get("job_description_filename"),
        resume_char_count=len(resume_text),
        job_description_char_count=len(job_description_text),
        updated_at=context.get("updated_at"),
        resume_preview=make_preview(resume_text),
        job_description_preview=make_preview(job_description_text),
    )


def update_resume_context(text: str, filename: str) -> None:
    context = load_context()
    context["resume_text"] = text
    context["resume_filename"] = filename
    _save_context(context)


def update_job_description_context(text: str, filename: str) -> None:
    context = load_context()
    context["job_description_text"] = text
    context["job_description_filename"] = filename
    _save_context(context)


def clear_context() -> None:
    if CONTEXT_PATH.exists():
        CONTEXT_PATH.unlink()


def _save_context(context: dict[str, Any]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    context["updated_at"] = datetime.now(timezone.utc).isoformat()
    with CONTEXT_PATH.open("w", encoding="utf-8") as context_file:
        json.dump(context, context_file, indent=2)
