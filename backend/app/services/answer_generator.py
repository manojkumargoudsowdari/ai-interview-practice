import json
import re
from typing import Any

import httpx

from app.config import settings
from app.schemas import PracticeAnswerGenerateRequest, PracticeAnswerGenerateResponse
from app.services.context_store import load_context


SYSTEM_PROMPT = """You are an AI interview practice coach.
Generate one concise first-person practice answer the candidate can read out loud.
Do not generate a full interview script or multiple options.
Use the candidate's resume/JD context when available.
Do not invent candidate experience, employers, metrics, tools, or project facts.
If direct experience is missing or only high-level context is provided, say "related experience" or explain a "conceptual approach."
Prefer "I would" phrasing unless the resume context explicitly supports a direct "I did" claim.
Do not claim measurable improvements, delivered outcomes, or production wins unless those facts appear in the resume context.
Keep the answer practical, natural, and interview-ready.
Return strict JSON only.
The answer should be 140 to 220 words.
Warnings should be short and only mention missing context or fallback behavior."""


def generate_practice_answer(request: PracticeAnswerGenerateRequest) -> PracticeAnswerGenerateResponse:
    if not request.question.strip():
        raise ValueError("Question cannot be empty.")

    resume_context, job_description = _resolve_context(request)
    provider = settings.llm_provider.strip().lower()

    if provider == "ollama":
        return _generate_ollama_answer(request, resume_context, job_description)

    if provider != "mock":
        print(f"Unsupported LLM_PROVIDER '{settings.llm_provider}'. Using mock answer fallback.")

    return _generate_mock_answer(
        request=request,
        provider="mock",
        warnings=_context_warnings(resume_context, job_description),
    )


def _resolve_context(request: PracticeAnswerGenerateRequest) -> tuple[str | None, str | None]:
    resume_context = request.resume_context
    job_description = request.job_description

    if request.use_saved_context and not resume_context and not job_description:
        context = load_context()
        resume_context = context.get("resume_text") or None
        job_description = context.get("job_description_text") or None

    return resume_context, job_description


def _generate_ollama_answer(
    request: PracticeAnswerGenerateRequest,
    resume_context: str | None,
    job_description: str | None,
) -> PracticeAnswerGenerateResponse:
    base_url = settings.ollama_base_url.rstrip("/")
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(request, resume_context, job_description)},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.2},
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(f"{base_url}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"]["content"]
    except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Ollama answer generation failed. Using fallback answer. Error: {exc}")
        return _generate_mock_answer(
            request=request,
            provider="ollama-fallback",
            warnings=_context_warnings(resume_context, job_description)
            + ["Ollama unavailable; used fallback practice answer."],
        )

    try:
        parsed = _parse_json_content(content)
        answer = str(parsed.get("answer") or "").strip()
        warnings = _string_list(parsed.get("warnings"))
        if not answer:
            raise ValueError("LLM response must include answer.")

        return PracticeAnswerGenerateResponse(
            provider="ollama",
            answer=answer,
            warnings=(warnings + _context_warnings(resume_context, job_description))[:4],
        )
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        print(f"Ollama answer response parsing failed. Using fallback answer. Error: {exc}")
        return _generate_mock_answer(
            request=request,
            provider="ollama-fallback",
            warnings=_context_warnings(resume_context, job_description)
            + ["LLM response parsing failed; used fallback practice answer."],
        )


def _generate_mock_answer(
    request: PracticeAnswerGenerateRequest,
    provider: str,
    warnings: list[str] | None = None,
) -> PracticeAnswerGenerateResponse:
    question = request.question.strip()
    category = (request.category or "").lower()
    expected_angle = request.expected_answer_angle or "focus on the problem, actions, tools, and outcome"

    if "spark" in question.lower() or "pyspark" in question.lower() or "spark" in category:
        answer = (
            "My answer would start with how I diagnose the job before tuning it. "
            "In related data engineering work, I would first review Spark UI stages, executor usage, shuffle volume, "
            "skewed tasks, and file sizes to identify whether the bottleneck is data layout, joins, partitioning, or code logic. "
            "Then I would make targeted changes such as filtering early, reducing wide transformations, tuning partitions, "
            "handling skew, using broadcast joins where appropriate, and keeping Delta or Parquet files at efficient sizes. "
            "I would also validate the change with before-and-after runtime, failure rate, and data quality checks instead of "
            "assuming the tuning worked. The key point is that I do not optimize blindly. I connect the technical fix to a "
            f"production outcome, such as a more reliable pipeline, better SLA performance, or lower compute cost. For this question, I would emphasize {expected_angle}."
        )
    elif "behavioral" in category or "conflict" in question.lower() or "challenge" in question.lower():
        answer = (
            "I would answer this with a clear situation, action, and result. "
            "In a related professional situation, I would explain the context briefly, then focus on the specific role I played, "
            "how I communicated with stakeholders, and how I kept the work moving without blaming others. "
            "For example, if there was a production issue or disagreement on approach, I would clarify the impact, gather facts from logs or requirements, "
            "align the team on the highest-priority fix, and follow up with prevention steps. "
            "I would keep the tone accountable and practical. The strongest version of this answer should show ownership, communication, "
            "technical judgment, and learning. I would avoid overstating direct experience and phrase unsupported details as related experience or my conceptual approach."
        )
    else:
        answer = (
            "I would give a direct answer first, then support it with a practical project-style example. "
            "In related data engineering work, I would start by understanding the business requirement, data sources, volume, freshness expectations, "
            "and quality rules. From there, I would design the pipeline or solution using the right tools, keep the implementation observable, "
            "and validate the output with testing and reconciliation. If the question is about a tool or architecture, I would explain why that choice fits, "
            "what tradeoffs I considered, and how I would operate it in production. "
            "I would close with impact: reliability, data quality, faster delivery, simpler operations, or better downstream analytics. "
            f"For this specific question, I would make sure my answer covers {expected_angle} while staying honest about direct versus related experience."
        )

    return PracticeAnswerGenerateResponse(
        provider=provider,
        answer=answer,
        warnings=warnings or [],
    )


def _build_user_prompt(
    request: PracticeAnswerGenerateRequest,
    resume_context: str | None,
    job_description: str | None,
) -> str:
    return f"""Practice question:
{request.question}

Category:
{request.category or "Not provided"}

Difficulty:
{request.difficulty or "Not provided"}

Interviewer intent:
{request.interviewer_intent or "Not provided"}

Expected answer angle:
{request.expected_answer_angle or "Not provided"}

Follow-up questions:
{json.dumps(request.follow_up_questions[:3])}

Resume context:
{_truncate_context(resume_context)}

Job description context:
{_truncate_context(job_description)}

Expected JSON schema:
{{
  "answer": "first-person practice answer",
  "warnings": ["short warning if context is missing or unsupported"]
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
        raise ValueError("LLM answer response JSON must be an object.")

    return parsed


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []

    return [str(item).strip() for item in value if str(item).strip()]


def _context_warnings(resume_context: str | None, job_description: str | None) -> list[str]:
    warnings = []
    if not resume_context:
        warnings.append("No saved resume context was available; answer uses related experience phrasing.")
    if not job_description:
        warnings.append("No saved job description context was available; answer stays generic.")
    return warnings
