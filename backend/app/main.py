from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    AnswerScoringRequest,
    AnswerScoringResponse,
    CueGenerationRequest,
    CueGenerationResponse,
    LLMHealthResponse,
    PracticeAnswerGenerateRequest,
    PracticeAnswerGenerateResponse,
    PracticeAnswerScore,
    PracticeAnswerSubmitRequest,
    PracticeAnswerSubmitResponse,
    PracticeContextRequest,
    PracticeContextResponse,
    PracticeSessionQuestion,
    PracticeSessionStartRequest,
    PracticeSessionStartResponse,
    PracticeSessionStoreResponse,
    PracticeSessionSummaryResponse,
    QuestionBankGenerateRequest,
    QuestionBankGenerateResponse,
    QuestionBankStoreResponse,
    QuestionDetectionResponse,
    TranscriptRequest,
    UploadedDocumentResponse,
    VoicePracticeRequest,
    VoicePracticeResponse,
)
from app.services.context_store import (
    clear_context,
    get_context_response,
    load_context,
    update_job_description_context,
    update_resume_context,
)
from app.services.answer_generator import generate_practice_answer
from app.services.document_processor import (
    DocumentProcessingError,
    process_text_payload,
    process_uploaded_file,
)
from app.services.cue_generator import generate_rule_based_cues
from app.services.llm_service import generate_interview_cues, get_llm_health
from app.services.practice_session_store import (
    clear_sessions,
    create_session,
    load_all_sessions,
    load_session,
    next_question_for_session,
    submit_answer,
    summarize_session,
)
from app.services.question_bank_generator import generate_question_bank
from app.services.question_bank_store import clear_question_bank, load_question_bank, save_question_bank
from app.services.question_detector import detect_question
from app.services.scoring import score_answer


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "app": settings.app_name,
        "env": settings.app_env,
        "status": "running",
    }


@app.post("/detect-question", response_model=QuestionDetectionResponse)
def detect_question_api(request: TranscriptRequest):
    return detect_question(request.transcript)


@app.post("/generate-cues", response_model=CueGenerationResponse)
def generate_cues_api(request: CueGenerationRequest):
    context = load_context()
    resume_context = request.resume_context or context.get("resume_text") or None
    job_description = request.job_description or context.get("job_description_text") or None

    response = generate_interview_cues(
        question=request.question,
        resume_context=resume_context,
        job_description=job_description,
    )
    if any(_is_question_like_cue(cue) for cue in response.cue_points):
        return generate_rule_based_cues(
            question=request.question,
            resume_context=resume_context,
            job_description=job_description,
            provider=response.provider,
            risk_flags=(
                response.risk_flags
                + ["Generated question-form cue points were normalized to short fallback cues."]
            )[:3],
            follow_up_questions=(response.follow_up_questions + response.cue_points)[:3],
        )

    return response


def _is_question_like_cue(value: str) -> bool:
    lowered = value.strip().lower()
    question_starters = ("what ", "why ", "how ", "when ", "where ", "which ", "can ", "could ", "would ", "do ", "did ")
    return "?" in lowered or lowered.startswith(question_starters)


@app.get("/llm/health", response_model=LLMHealthResponse)
def llm_health_api():
    return get_llm_health()


@app.post("/score-answer", response_model=AnswerScoringResponse)
def score_answer_api(request: AnswerScoringRequest):
    return score_answer(
        question=request.question,
        answer=request.answer,
        job_description=request.job_description,
    )


@app.post("/upload/resume", response_model=UploadedDocumentResponse)
async def upload_resume_api(file: UploadFile = File(...)):
    try:
        document = await process_uploaded_file(file)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_resume_context(document.text, document.filename)
    return UploadedDocumentResponse(
        status="resume_uploaded",
        filename=document.filename,
        source="file",
        character_count=document.character_count,
        preview=document.preview,
    )


@app.post("/upload/job-description-file", response_model=UploadedDocumentResponse)
async def upload_job_description_file_api(file: UploadFile = File(...)):
    try:
        document = await process_uploaded_file(file)
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_job_description_context(document.text, document.filename)
    return UploadedDocumentResponse(
        status="job_description_uploaded",
        filename=document.filename,
        source="file",
        character_count=document.character_count,
        preview=document.preview,
    )


@app.post("/upload/job-description-text", response_model=UploadedDocumentResponse)
def upload_job_description_text_api(request: PracticeContextRequest):
    try:
        document = process_text_payload(request.text, request.source or "pasted_text")
    except DocumentProcessingError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    update_job_description_context(document.text, document.filename)
    return UploadedDocumentResponse(
        status="job_description_saved",
        filename=document.filename,
        source=document.filename,
        character_count=document.character_count,
        preview=document.preview,
    )


@app.get("/context", response_model=PracticeContextResponse)
def get_context_api():
    return get_context_response()


@app.delete("/context")
def clear_context_api():
    clear_context()
    return {"status": "context_cleared"}


@app.post("/question-bank/generate", response_model=QuestionBankGenerateResponse)
def generate_question_bank_api(request: QuestionBankGenerateRequest):
    response = generate_question_bank(request)
    save_question_bank(response)
    return response


@app.get("/question-bank", response_model=QuestionBankStoreResponse)
def get_question_bank_api():
    return load_question_bank()


@app.delete("/question-bank")
def clear_question_bank_api():
    clear_question_bank()
    return {"status": "question_bank_cleared"}


@app.post("/practice/start", response_model=PracticeSessionStartResponse)
def start_practice_session_api(request: PracticeSessionStartRequest):
    try:
        return create_session(
            category_filter=request.category_filter,
            difficulty_filter=request.difficulty_filter,
            max_questions=request.max_questions,
            shuffle=request.shuffle,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/practice/answer", response_model=PracticeAnswerSubmitResponse)
def submit_practice_answer_api(request: PracticeAnswerSubmitRequest):
    if not request.answer.strip():
        raise HTTPException(status_code=400, detail="Answer cannot be empty.")

    session_summary = None
    try:
        session_summary = summarize_session(request.session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    current_history_ids = {
        item.get("question", {}).get("id")
        for item in session_summary.history
        if item.get("question")
    }
    if request.question_id in current_history_ids:
        raise HTTPException(status_code=400, detail="Question has already been answered.")

    current_question = _find_current_question_from_summary(session_summary, request.question_id)
    if current_question is None:
        raise HTTPException(status_code=400, detail="Submitted question does not match the current session question.")

    scored = score_answer(
        question=current_question.question,
        answer=request.answer,
        job_description=current_question.expected_answer_angle,
    )
    score_payload = PracticeAnswerScore(
        score=scored.score,
        strengths=scored.strengths,
        improvements=scored.improvements,
        improved_answer=scored.improved_answer,
    )

    try:
        session = submit_answer(
            session_id=request.session_id,
            question_id=request.question_id,
            answer=request.answer,
            score_payload=score_payload,
        )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    next_question = next_question_for_session(session)
    answered = len(session.get("history", []))
    total = len(session.get("questions", []))
    return PracticeAnswerSubmitResponse(
        session_id=request.session_id,
        question_id=request.question_id,
        score=score_payload,
        next_question=next_question,
        completed=bool(session.get("completed", False)),
        progress=f"{answered}/{total}",
    )


@app.post("/practice/generate-answer", response_model=PracticeAnswerGenerateResponse)
def generate_practice_answer_api(request: PracticeAnswerGenerateRequest):
    try:
        return generate_practice_answer(request)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/voice-practice/process-transcript", response_model=VoicePracticeResponse)
def process_voice_practice_transcript_api(request: VoicePracticeRequest):
    transcript = request.transcript.strip()
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript cannot be empty.")

    detection = detect_question(transcript)
    if not detection.is_question or not detection.question:
        return VoicePracticeResponse(
            transcript=transcript,
            detection=detection,
            generated_answer=None,
            message="Transcript was captured, but no interview question was detected.",
        )

    answer_request = PracticeAnswerGenerateRequest(
        question=detection.question,
        category=detection.category,
        interviewer_intent="Answer the detected spoken interview question clearly.",
        expected_answer_angle="direct answer, relevant experience or conceptual approach, tools, and impact",
        use_saved_context=request.use_saved_context,
        resume_context=request.resume_context,
        job_description=request.job_description,
    )
    generated_answer = generate_practice_answer(answer_request)
    return VoicePracticeResponse(
        transcript=transcript,
        detection=detection,
        generated_answer=generated_answer,
        message="Question detected and practice answer generated.",
    )


@app.get("/practice/session/{session_id}", response_model=PracticeSessionSummaryResponse)
def get_practice_session_api(session_id: str):
    try:
        return summarize_session(session_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/practice/sessions", response_model=PracticeSessionStoreResponse)
def get_practice_sessions_api():
    return load_all_sessions()


@app.delete("/practice/sessions")
def clear_practice_sessions_api():
    clear_sessions()
    return {"status": "practice_sessions_cleared"}


def _find_current_question_from_summary(
    summary: PracticeSessionSummaryResponse,
    question_id: str,
) -> PracticeSessionQuestion | None:
    if summary.completed:
        return None

    answered_ids = {
        item.get("question", {}).get("id")
        for item in summary.history
        if item.get("question")
    }
    if question_id in answered_ids:
        return None

    # The current question itself is validated again inside submit_answer.
    # This lookup provides the question text for scoring before persistence.
    session = load_session(summary.session_id)
    if session is None:
        return None
    current_index = int(session.get("current_index", 0))
    questions = session.get("questions", [])
    if current_index >= len(questions):
        return None
    question = questions[current_index]
    if question.get("id") != question_id:
        return None
    return PracticeSessionQuestion.model_validate(question)
