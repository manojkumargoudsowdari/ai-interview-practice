import json
import re
from typing import Any

import httpx

from app.config import settings
from app.schemas import CueGenerationResponse, LLMHealthResponse
from app.services.cue_generator import generate_rule_based_cues


SYSTEM_PROMPT = """You are an AI interview practice coach.
Generate short cue points only.
Do not generate a full answer paragraph.
Use the candidate's resume/JD context when available.
Do not invent experience.
If direct experience is missing, phrase cues as "related experience" or "conceptual approach."
Return strict JSON only.
Max 8 cue_points.
Max 3 risk_flags.
Max 3 follow_up_questions.
short_direction should be one sentence."""


def generate_interview_cues(
    question: str,
    resume_context: str | None = None,
    job_description: str | None = None,
) -> CueGenerationResponse:
    provider = settings.llm_provider.strip().lower()

    if provider == "mock":
        return generate_rule_based_cues(
            question=question,
            resume_context=resume_context,
            job_description=job_description,
            provider="mock",
        )

    if provider == "ollama":
        return _generate_ollama_cues(
            question=question,
            resume_context=resume_context,
            job_description=job_description,
        )

    print(f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Using mock fallback.")
    return generate_rule_based_cues(
        question=question,
        resume_context=resume_context,
        job_description=job_description,
        provider="mock",
        risk_flags=[f"Unsupported LLM provider '{settings.llm_provider}'; used fallback cues."],
    )


def get_llm_health() -> LLMHealthResponse:
    provider = settings.llm_provider.strip().lower()

    if provider == "mock":
        return LLMHealthResponse(
            provider="mock",
            configured=True,
            available=True,
            message="Mock provider is configured and available.",
        )

    if provider != "ollama":
        return LLMHealthResponse(
            provider=settings.llm_provider,
            configured=False,
            available=False,
            message=f"Unsupported LLM provider '{settings.llm_provider}'.",
        )

    base_url = _clean_base_url(settings.ollama_base_url)
    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(f"{base_url}/api/tags")
            response.raise_for_status()
    except httpx.HTTPError as exc:
        return LLMHealthResponse(
            provider="ollama",
            configured=True,
            available=False,
            ollama_base_url=base_url,
            ollama_model=settings.ollama_model,
            message=f"Ollama is configured but unavailable: {exc}",
        )

    return LLMHealthResponse(
        provider="ollama",
        configured=True,
        available=True,
        ollama_base_url=base_url,
        ollama_model=settings.ollama_model,
        message="Ollama is reachable.",
    )


def _generate_ollama_cues(
    question: str,
    resume_context: str | None = None,
    job_description: str | None = None,
) -> CueGenerationResponse:
    base_url = _clean_base_url(settings.ollama_base_url)
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(question, resume_context, job_description)},
        ],
        "stream": False,
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"]["content"]
    except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Ollama cue generation failed. Using fallback cues. Error: {exc}")
        return generate_rule_based_cues(
            question=question,
            resume_context=resume_context,
            job_description=job_description,
            provider="mock",
            risk_flags=["Ollama unavailable; used fallback cues."],
        )

    try:
        parsed = _parse_json_content(content)
        return _cue_response_from_llm_json(question, parsed)
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Ollama response parsing failed. Using fallback cues. Error: {exc}")
        return generate_rule_based_cues(
            question=question,
            resume_context=resume_context,
            job_description=job_description,
            provider="mock",
            risk_flags=["LLM response parsing failed; used fallback cues."],
        )


def _build_user_prompt(
    question: str,
    resume_context: str | None,
    job_description: str | None,
) -> str:
    return f"""Interview question:
{question}

Resume context:
{_truncate_context(resume_context)}

Job description context:
{_truncate_context(job_description)}

Expected JSON schema:
{{
  "cue_points": ["short cue", "short cue"],
  "short_direction": "one sentence direction",
  "risk_flags": ["risk flag"],
  "follow_up_questions": ["follow-up question"]
}}"""


def _truncate_context(value: str | None, max_chars: int = 4000) -> str:
    if not value or not value.strip():
        return "No context provided."

    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= max_chars:
        return cleaned

    return f"{cleaned[:max_chars].rstrip()}... [truncated]"


def _parse_json_content(content: str) -> dict[str, Any]:
    cleaned = content.strip()

    fenced_match = re.search(r"```(?:json)?\s*(.*?)```", cleaned, flags=re.DOTALL | re.IGNORECASE)
    if fenced_match:
        cleaned = fenced_match.group(1).strip()

    if not cleaned.startswith("{"):
        start = cleaned.find("{")
        end = cleaned.rfind("}")
        if start != -1 and end != -1 and start < end:
            cleaned = cleaned[start : end + 1]

    parsed = json.loads(cleaned)
    if not isinstance(parsed, dict):
        raise ValueError("LLM response JSON must be an object.")

    return parsed


def _cue_response_from_llm_json(question: str, parsed: dict[str, Any]) -> CueGenerationResponse:
    cue_points = _string_list(parsed.get("cue_points"))[:8]
    short_direction = str(parsed.get("short_direction") or "").strip()
    risk_flags = _string_list(parsed.get("risk_flags"))[:3]
    follow_up_questions = _string_list(parsed.get("follow_up_questions"))[:3]

    if not cue_points or not short_direction:
        raise ValueError("LLM response must include cue_points and short_direction.")

    return CueGenerationResponse(
        question=question,
        cue_points=cue_points,
        short_direction=short_direction,
        risk_flags=risk_flags,
        follow_up_questions=follow_up_questions,
        provider="ollama",
    )


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _clean_base_url(value: str) -> str:
    return value.rstrip("/")
