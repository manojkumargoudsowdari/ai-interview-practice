import json
import random
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

from app.schemas import (
    PracticeAnswerScore,
    PracticeSessionQuestion,
    PracticeSessionStartResponse,
    PracticeSessionSummaryResponse,
    PracticeSessionStoreResponse,
    QuestionBankItem,
)
from app.services.question_bank_store import load_question_bank_response


BACKEND_DIR = Path(__file__).resolve().parents[2]
PROCESSED_DIR = BACKEND_DIR / "data" / "processed"
PRACTICE_SESSIONS_PATH = PROCESSED_DIR / "practice_sessions.json"


def create_session(
    category_filter: str | None,
    difficulty_filter: str | None,
    max_questions: int,
    shuffle: bool,
) -> PracticeSessionStartResponse:
    question_bank, _updated_at = load_question_bank_response()
    if question_bank is None or not question_bank.questions:
        raise ValueError("No question bank found. Generate a question bank first.")

    questions = _apply_filters(question_bank.questions, category_filter, difficulty_filter)
    if not questions:
        raise ValueError("No questions matched the selected filters.")

    if shuffle:
        random.shuffle(questions)

    clamped_max = max(1, min(50, max_questions))
    selected_questions = questions[:clamped_max]
    session_id = str(uuid4())
    session = {
        "session_id": session_id,
        "created_at": _now(),
        "question_ids": [question.id for question in selected_questions],
        "questions": [_question_to_session_question(question).model_dump() for question in selected_questions],
        "current_index": 0,
        "history": [],
        "completed": False,
    }

    sessions = _load_sessions_payload()
    sessions[session_id] = session
    _save_sessions_payload(sessions)

    return PracticeSessionStartResponse(
        session_id=session_id,
        total_questions=len(selected_questions),
        current_index=0,
        current_question=PracticeSessionQuestion.model_validate(session["questions"][0]),
        message="Practice session started.",
    )


def load_session(session_id: str) -> dict[str, Any] | None:
    return _load_sessions_payload().get(session_id)


def save_session(session: dict[str, Any]) -> None:
    sessions = _load_sessions_payload()
    sessions[session["session_id"]] = session
    _save_sessions_payload(sessions)


def submit_answer(
    session_id: str,
    question_id: str,
    answer: str,
    score_payload: PracticeAnswerScore,
) -> dict[str, Any]:
    session = load_session(session_id)
    if session is None:
        raise ValueError("Practice session not found.")
    if session.get("completed"):
        raise ValueError("Practice session is already completed.")

    questions = session.get("questions", [])
    current_index = int(session.get("current_index", 0))
    if current_index >= len(questions):
        session["completed"] = True
        save_session(session)
        raise ValueError("Practice session is already completed.")

    current_question = questions[current_index]
    if current_question["id"] != question_id:
        raise ValueError("Submitted question does not match the current session question.")

    history_item = {
        "question": current_question,
        "answer": answer,
        "score": score_payload.model_dump(),
        "answered_at": _now(),
    }
    session["history"].append(history_item)
    session["current_index"] = current_index + 1
    session["completed"] = session["current_index"] >= len(questions)
    save_session(session)
    return session


def summarize_session(session_id: str) -> PracticeSessionSummaryResponse:
    session = load_session(session_id)
    if session is None:
        raise ValueError("Practice session not found.")
    return _summarize(session)


def load_all_sessions() -> PracticeSessionStoreResponse:
    sessions = _load_sessions_payload()
    if not sessions:
        return PracticeSessionStoreResponse(
            has_sessions=False,
            total_sessions=0,
            latest_session_id=None,
            latest_summary=None,
        )

    latest = max(sessions.values(), key=lambda item: item.get("created_at", ""))
    latest_session_id = latest["session_id"]
    return PracticeSessionStoreResponse(
        has_sessions=True,
        total_sessions=len(sessions),
        latest_session_id=latest_session_id,
        latest_summary=_summarize(latest),
    )


def clear_sessions() -> None:
    if PRACTICE_SESSIONS_PATH.exists():
        PRACTICE_SESSIONS_PATH.unlink()


def next_question_for_session(session: dict[str, Any]) -> PracticeSessionQuestion | None:
    current_index = int(session.get("current_index", 0))
    questions = session.get("questions", [])
    if current_index >= len(questions):
        return None
    return PracticeSessionQuestion.model_validate(questions[current_index])


def _apply_filters(
    questions: list[QuestionBankItem],
    category_filter: str | None,
    difficulty_filter: str | None,
) -> list[QuestionBankItem]:
    category = (category_filter or "all").strip().lower()
    difficulty = (difficulty_filter or "mixed").strip().lower()

    filtered = questions
    if category and category != "all":
        filtered = [question for question in filtered if question.category.lower() == category]
    if difficulty and difficulty != "mixed":
        filtered = [question for question in filtered if question.difficulty.lower() == difficulty]
    return filtered


def _question_to_session_question(question: QuestionBankItem) -> PracticeSessionQuestion:
    return PracticeSessionQuestion(
        id=question.id,
        category=question.category,
        difficulty=question.difficulty,
        question=question.question,
        interviewer_intent=question.interviewer_intent,
        expected_answer_angle=question.expected_answer_angle,
        follow_up_questions=question.follow_up_questions,
    )


def _summarize(session: dict[str, Any]) -> PracticeSessionSummaryResponse:
    history = session.get("history", [])
    scores = [float(item["score"]["score"]) for item in history if "score" in item]
    average_score = round(sum(scores) / len(scores), 2) if scores else None

    category_scores: dict[str, list[float]] = defaultdict(list)
    for item in history:
        category = item.get("question", {}).get("category")
        score = item.get("score", {}).get("score")
        if category and score is not None:
            category_scores[category].append(float(score))

    weak_categories = [
        category
        for category, values in category_scores.items()
        if values and (sum(values) / len(values)) < 7.0
    ]
    strong_categories = [
        category
        for category, values in category_scores.items()
        if values and (sum(values) / len(values)) >= 8.0
    ]

    return PracticeSessionSummaryResponse(
        session_id=session["session_id"],
        total_questions=len(session.get("questions", [])),
        answered_questions=len(history),
        average_score=average_score,
        weak_categories=weak_categories,
        strong_categories=strong_categories,
        history=history,
        completed=bool(session.get("completed", False)),
    )


def _load_sessions_payload() -> dict[str, Any]:
    if not PRACTICE_SESSIONS_PATH.exists():
        return {}

    try:
        with PRACTICE_SESSIONS_PATH.open("r", encoding="utf-8") as sessions_file:
            payload = json.load(sessions_file)
    except (OSError, json.JSONDecodeError):
        return {}

    if not isinstance(payload, dict):
        return {}
    return payload


def _save_sessions_payload(payload: dict[str, Any]) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with PRACTICE_SESSIONS_PATH.open("w", encoding="utf-8") as sessions_file:
        json.dump(payload, sessions_file, indent=2)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()
