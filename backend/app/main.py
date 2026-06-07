from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    AnswerScoringRequest,
    AnswerScoringResponse,
    CueGenerationRequest,
    CueGenerationResponse,
    LLMHealthResponse,
    PracticeContextRequest,
    PracticeContextResponse,
    QuestionBankGenerateRequest,
    QuestionBankGenerateResponse,
    QuestionBankStoreResponse,
    QuestionDetectionResponse,
    TranscriptRequest,
    UploadedDocumentResponse,
)
from app.services.context_store import (
    clear_context,
    get_context_response,
    load_context,
    update_job_description_context,
    update_resume_context,
)
from app.services.document_processor import (
    DocumentProcessingError,
    process_text_payload,
    process_uploaded_file,
)
from app.services.cue_generator import generate_rule_based_cues
from app.services.llm_service import generate_interview_cues, get_llm_health
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
