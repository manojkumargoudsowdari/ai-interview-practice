from app.schemas import QuestionDetectionResponse


QUESTION_STARTERS = (
    "what",
    "why",
    "how",
    "when",
    "where",
    "which",
    "can you",
    "could you",
    "would you",
    "tell me",
    "walk me through",
    "explain",
    "describe",
    "have you",
    "do you",
    "did you",
)


def detect_question(transcript: str) -> QuestionDetectionResponse:
    text = transcript.strip()
    lower_text = text.lower()

    is_question = text.endswith("?") or lower_text.startswith(QUESTION_STARTERS)

    if not is_question:
        return QuestionDetectionResponse(
            is_question=False,
            question=None,
            category=None,
            topic=None,
        )

    category = "technical"
    topic = "general"

    if "spark" in lower_text or "pyspark" in lower_text:
        topic = "Spark / PySpark"
    elif "databricks" in lower_text or "delta" in lower_text:
        topic = "Databricks / Delta Lake"
    elif "rag" in lower_text or "retrieval" in lower_text or "embedding" in lower_text:
        topic = "RAG / AI"
    elif "pipeline" in lower_text or "etl" in lower_text:
        topic = "ETL / Data Pipelines"
    elif "production" in lower_text or "issue" in lower_text or "failure" in lower_text:
        topic = "Production Support"
    elif "tell me about yourself" in lower_text or "background" in lower_text:
        category = "intro"
        topic = "Resume Walkthrough"
    elif "conflict" in lower_text or "challenge" in lower_text or "leadership" in lower_text:
        category = "behavioral"
        topic = "Behavioral"

    return QuestionDetectionResponse(
        is_question=True,
        question=text,
        category=category,
        topic=topic,
    )
