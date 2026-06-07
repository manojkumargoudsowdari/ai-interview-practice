import json
import re
from typing import Any
from uuid import uuid4

import httpx

from app.config import settings
from app.schemas import QuestionBankGenerateRequest, QuestionBankGenerateResponse, QuestionBankItem
from app.services.context_store import load_context


QUESTION_CATEGORIES = [
    "Resume walkthrough",
    "Project deep dive",
    "Spark / PySpark",
    "Databricks / Delta Lake",
    "ETL / pipelines",
    "Production support",
    "Data modeling",
    "AI-ready datasets",
    "RAG / AI agents",
    "Behavioral",
    "Pressure follow-ups",
]

DIFFICULTIES = {"easy", "medium", "hard"}
MIN_QUESTIONS = 11
MAX_QUESTIONS = 110


SYSTEM_PROMPT = """You are an interview practice question generator.
Generate questions for a Senior Data Engineer candidate.
Use the resume and job description context.
Do not invent candidate experience.
Questions should be realistic and interview-style.
Include technical, project-based, behavioral, and pressure follow-up questions.
Return strict JSON only.
Use only the supported categories.
difficulty must be one of: easy, medium, hard.
follow_up_questions max 3 per question.
If resume/JD context is missing, include a warning and generate generic Senior Data Engineer questions."""


def generate_question_bank(request: QuestionBankGenerateRequest) -> QuestionBankGenerateResponse:
    total_questions = _clamp_total(request.total_questions)
    difficulty = _normalize_requested_difficulty(request.difficulty)
    resume_context, job_description, warnings = _resolve_context(request)
    provider = settings.llm_provider.strip().lower()

    if provider == "ollama":
        response = _generate_with_ollama(
            total_questions=total_questions,
            difficulty=difficulty,
            resume_context=resume_context,
            job_description=job_description,
            warnings=warnings,
        )
        if response is not None:
            return response

        return _generate_mock_bank(
            total_questions=total_questions,
            difficulty=difficulty,
            resume_context=resume_context,
            job_description=job_description,
            provider="ollama-fallback",
            warnings=warnings + ["Ollama question bank generation failed; used fallback questions."],
        )

    if provider != "mock":
        warnings = warnings + [f"Unsupported LLM provider '{settings.llm_provider}'; used fallback questions."]

    return _generate_mock_bank(
        total_questions=total_questions,
        difficulty=difficulty,
        resume_context=resume_context,
        job_description=job_description,
        provider="mock",
        warnings=warnings,
    )


def _generate_with_ollama(
    total_questions: int,
    difficulty: str,
    resume_context: str,
    job_description: str,
    warnings: list[str],
) -> QuestionBankGenerateResponse | None:
    payload = {
        "model": settings.ollama_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": _build_user_prompt(
                    total_questions=total_questions,
                    difficulty=difficulty,
                    resume_context=resume_context,
                    job_description=job_description,
                ),
            },
        ],
        "stream": False,
        "options": {"temperature": 0.2},
    }

    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds) as client:
            response = client.post(f"{settings.ollama_base_url.rstrip('/')}/api/chat", json=payload)
            response.raise_for_status()
            content = response.json()["message"]["content"]
    except (httpx.HTTPError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print(f"Ollama question bank generation failed. Error: {exc}")
        return None

    try:
        parsed = _parse_json_content(content)
        questions = _normalize_llm_questions(parsed.get("questions"), total_questions)
        llm_warnings = _string_list(parsed.get("warnings"))
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        print(f"Ollama question bank parsing failed. Error: {exc}")
        return None

    if len(questions) < total_questions:
        needed = total_questions - len(questions)
        fallback = _generate_mock_items(needed, difficulty, start_index=len(questions))
        questions.extend(fallback)
        llm_warnings.append("LLM returned fewer questions than requested; filled remainder with fallback questions.")

    return QuestionBankGenerateResponse(
        provider="ollama",
        total_questions=len(questions[:total_questions]),
        categories=_categories_for_questions(questions[:total_questions]),
        questions=questions[:total_questions],
        warnings=(warnings + llm_warnings)[:10],
    )


def _generate_mock_bank(
    total_questions: int,
    difficulty: str,
    resume_context: str,
    job_description: str,
    provider: str,
    warnings: list[str],
) -> QuestionBankGenerateResponse:
    if not resume_context.strip() and not job_description.strip():
        warnings = warnings + ["Resume/JD context is missing; generated generic Senior Data Engineer questions."]

    questions = _generate_mock_items(total_questions, difficulty)
    return QuestionBankGenerateResponse(
        provider=provider,
        total_questions=len(questions),
        categories=_categories_for_questions(questions),
        questions=questions,
        warnings=warnings,
    )


def _generate_mock_items(total_questions: int, difficulty: str, start_index: int = 0) -> list[QuestionBankItem]:
    templates = {
        "Resume walkthrough": [
            ("Walk me through your data engineering background and the kind of systems you have owned.", "Assess clarity of senior-level background.", "Summarize scope, tools, ownership, and measurable outcomes."),
            ("Which project on your resume best represents your senior data engineering work?", "Identify strongest project signal.", "Pick one relevant project and explain business context, architecture, and impact."),
            ("How would you connect your recent work to this role?", "Assess role alignment.", "Map related experience to JD responsibilities without overstating direct implementation."),
            ("What parts of your resume should I ask deeper technical questions about?", "Find depth areas.", "Highlight Spark, Databricks, pipelines, production support, and data quality."),
            ("Where do you want to grow next as a data engineer?", "Assess self-awareness.", "Connect growth areas to the target role and current strengths."),
        ],
        "Project deep dive": [
            ("Describe a data pipeline project from requirements through production release.", "Evaluate end-to-end delivery.", "Cover requirements, design, implementation, testing, deployment, and support."),
            ("What was the hardest technical tradeoff in one of your projects?", "Assess engineering judgment.", "Explain options considered, decision criteria, and outcome."),
            ("How did you validate that your project solved the right business problem?", "Assess product thinking.", "Discuss stakeholder alignment, metrics, data checks, and adoption."),
            ("Tell me about a project where the first design did not work.", "Assess iteration and debugging.", "Explain what failed, what you changed, and what you learned."),
            ("How would you explain one of your data projects to a non-technical stakeholder?", "Assess communication.", "Use business problem, data flow, and impact without heavy jargon."),
        ],
        "Spark / PySpark": [
            ("How did you optimize Spark jobs in practice?", "Assess Spark performance knowledge.", "Discuss Spark UI, shuffle, partitioning, skew, caching, file sizing, and measurable impact."),
            ("How do you debug a slow PySpark job?", "Assess troubleshooting process.", "Start with stages/tasks, data skew, joins, partitions, and resource usage."),
            ("When would you repartition versus coalesce?", "Assess practical Spark API knowledge.", "Explain shuffle cost, output file goals, and downstream read patterns."),
            ("How do you handle skewed joins in Spark?", "Assess advanced optimization.", "Discuss salting, broadcast joins, AQE, partitioning, and data distribution."),
            ("What mistakes commonly make Spark pipelines expensive?", "Assess cost awareness.", "Mention wide shuffles, small files, repeated scans, poor partitioning, and unnecessary actions."),
        ],
        "Databricks / Delta Lake": [
            ("How do you structure Bronze, Silver, and Gold layers in Databricks?", "Assess lakehouse design.", "Explain raw ingestion, cleansing, business-ready aggregates, and governance."),
            ("What Delta Lake features help with reliable pipelines?", "Assess Delta knowledge.", "Mention ACID transactions, schema enforcement, time travel, MERGE, and optimization."),
            ("How would you manage data quality in Databricks?", "Assess production readiness.", "Discuss expectations, quarantine, validation rules, alerts, and lineage."),
            ("How do Unity Catalog concepts affect pipeline design?", "Assess governance awareness.", "Discuss permissions, catalogs/schemas, lineage, and controlled access."),
            ("How do you reduce small file problems in Delta tables?", "Assess operational tuning.", "Mention optimized writes, compaction, partition strategy, and scheduled maintenance."),
        ],
        "ETL / pipelines": [
            ("How do you design an ETL pipeline for reliability?", "Assess pipeline architecture.", "Discuss idempotency, retries, checkpoints, validation, and observability."),
            ("How do you handle late-arriving or corrected source data?", "Assess data correctness.", "Mention incremental logic, MERGE/upsert, watermarks, reprocessing, and auditability."),
            ("What orchestration patterns have worked well for you?", "Assess workflow design.", "Discuss dependencies, retries, SLAs, backfills, and failure notifications."),
            ("How do you decide between batch and streaming?", "Assess architecture tradeoffs.", "Compare latency, cost, complexity, source behavior, and business need."),
            ("How do you make pipelines easy to support?", "Assess maintainability.", "Discuss clear ownership, logs, metrics, documentation, tests, and runbooks."),
        ],
        "Production support": [
            ("A critical pipeline failed before a business SLA. What do you do first?", "Assess incident response.", "Prioritize impact, logs, recent changes, rollback/retry, communication, and prevention."),
            ("How do you investigate bad data in production?", "Assess root-cause process.", "Trace lineage, source changes, validation gaps, affected consumers, and remediation."),
            ("Tell me about a production issue you resolved.", "Assess real operational experience.", "Use related experience or conceptual approach with root cause and prevention."),
            ("What monitoring would you add to a data platform?", "Assess observability.", "Mention freshness, volume, quality, schema drift, latency, cost, and SLA alerts."),
            ("How do you balance quick fixes and long-term prevention?", "Assess judgment under pressure.", "Separate mitigation, RCA, durable fix, and follow-up tracking."),
        ],
        "Data modeling": [
            ("How do you decide between star schema and wide denormalized tables?", "Assess modeling tradeoffs.", "Discuss query patterns, performance, governance, usability, and maintenance."),
            ("How do you model slowly changing dimensions?", "Assess warehouse concepts.", "Explain Type 1/Type 2 choices, effective dates, surrogate keys, and auditability."),
            ("What makes a data model easy for analysts to use?", "Assess user empathy.", "Discuss clear grain, naming, documentation, metrics definitions, and predictable joins."),
            ("How do you validate the grain of a fact table?", "Assess modeling precision.", "Define event/entity grain, keys, duplicates, and reconciliation."),
            ("How do you handle schema evolution in curated datasets?", "Assess change management.", "Discuss compatibility, migrations, versioning, and consumer communication."),
        ],
        "AI-ready datasets": [
            ("What makes a dataset AI-ready?", "Assess AI data foundation thinking.", "Discuss quality, lineage, permissions, freshness, documentation, and evaluation labels."),
            ("How would you prepare enterprise data for LLM use cases?", "Assess applied AI data design.", "Mention cleansing, chunking candidates, metadata, access control, and monitoring."),
            ("How do you prevent poor data quality from affecting AI outputs?", "Assess risk awareness.", "Discuss validation, trusted sources, grounding, evaluation, and feedback loops."),
            ("How do you design metadata for AI retrieval?", "Assess retrieval preparation.", "Mention source, owner, timestamp, entity, sensitivity, and business domain."),
            ("How do governance requirements change AI dataset design?", "Assess responsible implementation.", "Discuss access control, PII handling, lineage, retention, and auditability."),
        ],
        "RAG / AI agents": [
            ("Explain RAG to a data engineering interviewer.", "Assess conceptual clarity.", "Explain retrieval over trusted documents, embeddings, vector search, prompting, and evaluation."),
            ("How would you build a RAG pipeline over internal documentation?", "Assess practical design.", "Mention ingestion, chunking, embeddings, vector index, retrieval, citations, and monitoring."),
            ("What can go wrong in a RAG system?", "Assess risk awareness.", "Discuss stale documents, poor chunks, bad retrieval, hallucination, permissions, and evaluation gaps."),
            ("How do AI agents change data platform requirements?", "Assess emerging architecture thinking.", "Discuss tool access, observability, permissions, state, and human review."),
            ("How would you evaluate RAG answer quality?", "Assess validation approach.", "Mention golden questions, retrieval metrics, groundedness, human review, and regression tests."),
        ],
        "Behavioral": [
            ("Tell me about a conflict with a stakeholder or teammate.", "Assess collaboration.", "Use situation, action, tradeoff, and outcome without blaming."),
            ("Describe a time you had to learn a new technology quickly.", "Assess learning agility.", "Explain learning plan, applied project, and result."),
            ("How do you handle unclear requirements?", "Assess ambiguity management.", "Discuss clarifying questions, assumptions, prototypes, and written alignment."),
            ("Tell me about a time you influenced without authority.", "Assess leadership.", "Show data-driven communication, trust building, and outcome."),
            ("How do you mentor junior engineers?", "Assess senior behavior.", "Discuss reviews, pairing, standards, feedback, and independence."),
        ],
        "Pressure follow-ups": [
            ("Why should we believe you can handle this role if you have not done every listed requirement directly?", "Assess confidence and honesty.", "Use related experience, conceptual understanding, and learning plan without inventing experience."),
            ("What would you do if your optimization made performance worse?", "Assess pressure response.", "Discuss rollback, metrics, hypothesis testing, and root cause."),
            ("What is the weakest area in your profile for this job?", "Assess self-awareness.", "Name a real gap, adjacent strengths, and concrete improvement plan."),
            ("If I challenge your architecture choice, how would you defend it?", "Assess technical reasoning.", "Explain tradeoffs, evidence, constraints, and willingness to adjust."),
            ("What would you do in your first 30 days on this data team?", "Assess ramp-up plan.", "Focus on systems, stakeholders, SLAs, data quality, and quick wins."),
        ],
    }

    questions: list[QuestionBankItem] = []
    index = start_index
    while len(questions) < total_questions:
        category = QUESTION_CATEGORIES[index % len(QUESTION_CATEGORIES)]
        category_templates = templates[category]
        question, intent, angle = category_templates[(index // len(QUESTION_CATEGORIES)) % len(category_templates)]
        item_difficulty = _difficulty_for_index(index) if difficulty == "mixed" else difficulty
        questions.append(
            QuestionBankItem(
                id=f"qb-{index + 1:03d}-{uuid4().hex[:6]}",
                category=category,
                difficulty=item_difficulty,
                question=question,
                interviewer_intent=intent,
                expected_answer_angle=angle,
                follow_up_questions=_follow_ups_for_category(category),
            )
        )
        index += 1

    return questions


def _resolve_context(request: QuestionBankGenerateRequest) -> tuple[str, str, list[str]]:
    warnings: list[str] = []
    resume_context = request.resume_context or ""
    job_description = request.job_description or ""

    if request.use_saved_context:
        saved_context = load_context()
        resume_context = resume_context or saved_context.get("resume_text") or ""
        job_description = job_description or saved_context.get("job_description_text") or ""

    if not resume_context.strip():
        warnings.append("Resume context is missing.")
    if not job_description.strip():
        warnings.append("Job description context is missing.")

    return resume_context, job_description, warnings


def _build_user_prompt(
    total_questions: int,
    difficulty: str,
    resume_context: str,
    job_description: str,
) -> str:
    return f"""Generate exactly {total_questions} interview practice questions.
Requested difficulty: {difficulty}

Supported categories:
{json.dumps(QUESTION_CATEGORIES)}

Resume context:
{_truncate_context(resume_context)}

Job description context:
{_truncate_context(job_description)}

Expected strict JSON:
{{
  "questions": [
    {{
      "category": "Spark / PySpark",
      "difficulty": "medium",
      "question": "question text",
      "interviewer_intent": "what the interviewer is evaluating",
      "expected_answer_angle": "how the candidate should approach the answer",
      "follow_up_questions": ["follow-up", "follow-up"]
    }}
  ],
  "warnings": []
}}"""


def _normalize_llm_questions(value: Any, total_questions: int) -> list[QuestionBankItem]:
    if not isinstance(value, list):
        raise ValueError("Question bank JSON must include a questions list.")

    questions: list[QuestionBankItem] = []
    for index, raw_item in enumerate(value[:total_questions]):
        if not isinstance(raw_item, dict):
            continue

        category = str(raw_item.get("category") or "").strip()
        if category not in QUESTION_CATEGORIES:
            category = QUESTION_CATEGORIES[index % len(QUESTION_CATEGORIES)]

        difficulty = str(raw_item.get("difficulty") or "").strip().lower()
        if difficulty not in DIFFICULTIES:
            difficulty = _difficulty_for_index(index)

        question = str(raw_item.get("question") or "").strip()
        interviewer_intent = str(raw_item.get("interviewer_intent") or "").strip()
        expected_answer_angle = str(raw_item.get("expected_answer_angle") or "").strip()

        if not question or not interviewer_intent or not expected_answer_angle:
            continue

        questions.append(
            QuestionBankItem(
                id=f"qb-{index + 1:03d}-{uuid4().hex[:6]}",
                category=category,
                difficulty=difficulty,
                question=question,
                interviewer_intent=interviewer_intent,
                expected_answer_angle=expected_answer_angle,
                follow_up_questions=_string_list(raw_item.get("follow_up_questions"))[:3],
            )
        )

    if not questions:
        raise ValueError("No valid questions returned by LLM.")

    return questions


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
        raise ValueError("Question bank response must be a JSON object.")
    return parsed


def _clamp_total(value: int) -> int:
    return max(MIN_QUESTIONS, min(MAX_QUESTIONS, value))


def _normalize_requested_difficulty(value: str) -> str:
    normalized = value.strip().lower()
    if normalized in DIFFICULTIES or normalized == "mixed":
        return normalized
    return "mixed"


def _difficulty_for_index(index: int) -> str:
    return ["easy", "medium", "hard"][index % 3]


def _categories_for_questions(questions: list[QuestionBankItem]) -> list[str]:
    return [category for category in QUESTION_CATEGORIES if any(item.category == category for item in questions)]


def _follow_ups_for_category(category: str) -> list[str]:
    return [
        f"What was the measurable impact for {category.lower()}?",
        "What tradeoffs did you consider?",
    ]


def _truncate_context(value: str, max_chars: int = 4000) -> str:
    if not value.strip():
        return "No context provided."
    cleaned = re.sub(r"\s+", " ", value).strip()
    if len(cleaned) <= max_chars:
        return cleaned
    return f"{cleaned[:max_chars].rstrip()}... [truncated]"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value if str(item).strip()]
