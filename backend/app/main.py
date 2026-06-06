from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.schemas import (
    AnswerScoringRequest,
    AnswerScoringResponse,
    CueGenerationRequest,
    CueGenerationResponse,
    QuestionDetectionResponse,
    TranscriptRequest,
)
from app.services.cue_generator import generate_cues
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
    return generate_cues(
        question=request.question,
        resume_context=request.resume_context,
        job_description=request.job_description,
    )


@app.post("/score-answer", response_model=AnswerScoringResponse)
def score_answer_api(request: AnswerScoringRequest):
    return score_answer(
        question=request.question,
        answer=request.answer,
        job_description=request.job_description,
    )
