from app.schemas import CueGenerationResponse


def generate_rule_based_cues(
    question: str,
    resume_context: str | None = None,
    job_description: str | None = None,
    provider: str = "mock",
    risk_flags: list[str] | None = None,
    follow_up_questions: list[str] | None = None,
) -> CueGenerationResponse:
    q = question.lower()
    context = f"{resume_context or ''} {job_description or ''}".lower()
    has_context = bool(context.strip())

    if "spark" in q or "pyspark" in q or "optimize" in q:
        cues = ["Spark UI", "shuffle", "partitioning", "skew", "AQE", "file size", "result"]
        direction = "Start with diagnosis, explain tuning actions, then finish with measurable impact."

    elif "databricks" in q or "delta" in q:
        cues = ["Bronze/Silver/Gold", "Delta Lake", "Workflows", "DLT", "Unity Catalog", "quality", "SLA"]
        direction = "Connect Databricks architecture to governed, production-grade data pipelines."

    elif "rag" in q or "embedding" in q or "vector" in q:
        cues = ["documents", "chunking", "embeddings", "vector search", "retrieval", "LLM", "evaluation"]
        direction = "Explain RAG as grounded retrieval over trusted data, not just LLM prompting."

    elif "production" in q or "failure" in q or "issue" in q:
        cues = ["alert", "logs", "lineage", "bad data", "reprocess", "root cause", "prevention"]
        direction = "Use a production troubleshooting story with clear root cause and prevention."

    elif "your background" in q or "tell me about yourself" in q:
        cues = ["8+ years", "data engineering", "Databricks", "Spark", "Lakehouse", "banking/telecom", "AI-ready data"]
        direction = "Give a 60-90 second senior data engineer summary aligned to the JD."

    else:
        cues = ["direct answer", "project example", "tools", "challenge", "solution", "impact"]
        direction = "Answer using a project-based structure and avoid generic statements."

    if has_context:
        if "databricks" in context and "Databricks" not in cues:
            cues.append("Databricks")
        if "spark" in context and "Spark" not in cues and "Spark UI" not in cues:
            cues.append("Spark")
        if "azure" in context and "Azure" not in cues:
            cues.append("Azure")
        if "lead" in context or "senior" in context:
            cues.append("senior ownership")

    return CueGenerationResponse(
        question=question,
        cue_points=cues,
        short_direction=direction,
        risk_flags=risk_flags or [],
        follow_up_questions=follow_up_questions or [],
        provider=provider,
    )


def generate_cues(
    question: str,
    resume_context: str | None = None,
    job_description: str | None = None,
) -> CueGenerationResponse:
    return generate_rule_based_cues(
        question=question,
        resume_context=resume_context,
        job_description=job_description,
    )
