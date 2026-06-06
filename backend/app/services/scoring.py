from app.schemas import AnswerScoringResponse


def score_answer(
    question: str,
    answer: str,
    job_description: str | None = None,
) -> AnswerScoringResponse:
    answer_lower = answer.lower()

    score = 5.0
    strengths = []
    improvements = []

    if len(answer.split()) >= 60:
        score += 1.0
        strengths.append("You gave enough detail for a senior-level response.")
    else:
        improvements.append("Add more detail and include a real project example.")

    technical_keywords = ["spark", "databricks", "delta", "pipeline", "sql", "python", "quality", "production"]
    matched_keywords = [kw for kw in technical_keywords if kw in answer_lower]

    if len(matched_keywords) >= 3:
        score += 1.5
        strengths.append("You included relevant technical keywords.")
    else:
        improvements.append("Add more role-specific technical terms.")

    impact_keywords = ["improved", "reduced", "optimized", "sla", "performance", "cost", "latency", "quality"]
    if any(kw in answer_lower for kw in impact_keywords):
        score += 1.0
        strengths.append("You mentioned production or business impact.")
    else:
        improvements.append("Add measurable impact such as SLA, runtime, data quality, or performance improvement.")

    if "i " in answer_lower or answer_lower.startswith("i"):
        score += 0.5
        strengths.append("You answered in first person.")
    else:
        improvements.append("Use first-person language to sound natural and interview-ready.")

    score = min(score, 10.0)

    improved_answer = (
        "A stronger answer should start with a direct response, then give a real project example, "
        "mention the tools used, explain the challenge, describe your solution, and close with impact."
    )

    return AnswerScoringResponse(
        score=score,
        strengths=strengths,
        improvements=improvements,
        improved_answer=improved_answer,
    )
