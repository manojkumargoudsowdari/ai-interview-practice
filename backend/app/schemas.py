from typing import List, Optional

from pydantic import BaseModel


class TranscriptRequest(BaseModel):
    transcript: str
    resume_context: Optional[str] = None
    job_description: Optional[str] = None


class QuestionDetectionResponse(BaseModel):
    is_question: bool
    question: Optional[str] = None
    category: Optional[str] = None
    topic: Optional[str] = None


class CueGenerationRequest(BaseModel):
    question: str
    resume_context: Optional[str] = None
    job_description: Optional[str] = None


class CueGenerationResponse(BaseModel):
    question: str
    cue_points: List[str]
    short_direction: str


class UploadedDocumentResponse(BaseModel):
    status: str
    filename: Optional[str] = None
    source: str
    character_count: int
    preview: str


class PracticeContextRequest(BaseModel):
    text: str
    source: Optional[str] = "pasted_text"


class PracticeContextResponse(BaseModel):
    has_resume: bool
    has_job_description: bool
    resume_filename: Optional[str] = None
    job_description_filename: Optional[str] = None
    resume_char_count: int
    job_description_char_count: int
    updated_at: Optional[str] = None
    resume_preview: str
    job_description_preview: str


class AnswerScoringRequest(BaseModel):
    question: str
    answer: str
    job_description: Optional[str] = None


class AnswerScoringResponse(BaseModel):
    score: float
    strengths: List[str]
    improvements: List[str]
    improved_answer: str
