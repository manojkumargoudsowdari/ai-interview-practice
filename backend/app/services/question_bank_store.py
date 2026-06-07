import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.schemas import QuestionBankGenerateResponse, QuestionBankStoreResponse


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
QUESTION_BANK_PATH = PROCESSED_DIR / "question_bank.json"


def save_question_bank(response: QuestionBankGenerateResponse) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    payload = response.model_dump()
    payload["updated_at"] = datetime.now(timezone.utc).isoformat()

    with QUESTION_BANK_PATH.open("w", encoding="utf-8") as question_bank_file:
        json.dump(payload, question_bank_file, indent=2)


def load_question_bank() -> QuestionBankStoreResponse:
    if not QUESTION_BANK_PATH.exists():
        return QuestionBankStoreResponse(
            has_question_bank=False,
            total_questions=0,
            updated_at=None,
            preview=[],
        )

    try:
        with QUESTION_BANK_PATH.open("r", encoding="utf-8") as question_bank_file:
            payload: dict[str, Any] = json.load(question_bank_file)
    except (OSError, json.JSONDecodeError):
        return QuestionBankStoreResponse(
            has_question_bank=False,
            total_questions=0,
            updated_at=None,
            preview=[],
        )

    response = QuestionBankGenerateResponse.model_validate(payload)
    return QuestionBankStoreResponse(
        has_question_bank=bool(response.questions),
        total_questions=len(response.questions),
        updated_at=payload.get("updated_at"),
        preview=response.questions[:10],
    )


def clear_question_bank() -> None:
    if QUESTION_BANK_PATH.exists():
        QUESTION_BANK_PATH.unlink()
