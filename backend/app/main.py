from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    AnswerScoringRequest,
    AnswerScoringResponse,
    CueGenerationRequest,
    CueGenerationResponse,
    PracticeContextRequest,
    PracticeContextResponse,
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
from app.services.cue_generator import generate_cues
from app.services.document_processor import (
    DocumentProcessingError,
    process_text_payload,
    process_uploaded_file,
)
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

    return generate_cues(
        question=request.question,
        resume_context=resume_context,
        job_description=job_description,
    )


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
