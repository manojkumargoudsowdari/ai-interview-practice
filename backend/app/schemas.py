from typing import List, Optional

from pydantic import BaseModel, Field


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
    risk_flags: List[str] = Field(default_factory=list)
    follow_up_questions: List[str] = Field(default_factory=list)
    provider: str = "mock"


class LLMHealthResponse(BaseModel):
    provider: str
    configured: bool
    available: bool
    message: str
    ollama_base_url: Optional[str] = None
    ollama_model: Optional[str] = None


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


class QuestionBankItem(BaseModel):
    id: str
    category: str
    difficulty: str
    question: str
    interviewer_intent: str
    expected_answer_angle: str
    follow_up_questions: List[str] = Field(default_factory=list)


class QuestionBankGenerateRequest(BaseModel):
    total_questions: int = 55
    difficulty: str = "mixed"
    use_saved_context: bool = True
    resume_context: Optional[str] = None
    job_description: Optional[str] = None


class QuestionBankGenerateResponse(BaseModel):
    provider: str
    total_questions: int
    categories: List[str]
    questions: List[QuestionBankItem]
    warnings: List[str] = Field(default_factory=list)


class QuestionBankStoreResponse(BaseModel):
    has_question_bank: bool
    total_questions: int
    updated_at: Optional[str] = None
    preview: List[QuestionBankItem] = Field(default_factory=list)


class PracticeSessionStartRequest(BaseModel):
    category_filter: Optional[str] = None
    difficulty_filter: Optional[str] = None
    max_questions: int = 10
    shuffle: bool = True


class PracticeSessionQuestion(BaseModel):
    id: str
    category: str
    difficulty: str
    question: str
    interviewer_intent: str
    expected_answer_angle: str
    follow_up_questions: List[str] = Field(default_factory=list)


class PracticeSessionStartResponse(BaseModel):
    session_id: str
    total_questions: int
    current_index: int
    current_question: Optional[PracticeSessionQuestion]
    message: str


class PracticeAnswerSubmitRequest(BaseModel):
    session_id: str
    question_id: str
    answer: str


class PracticeAnswerScore(BaseModel):
    score: float
    strengths: List[str]
    improvements: List[str]
    improved_answer: str


class PracticeAnswerSubmitResponse(BaseModel):
    session_id: str
    question_id: str
    score: PracticeAnswerScore
    next_question: Optional[PracticeSessionQuestion]
    completed: bool
    progress: str


class PracticeSessionSummaryResponse(BaseModel):
    session_id: str
    total_questions: int
    answered_questions: int
    average_score: Optional[float]
    weak_categories: List[str]
    strong_categories: List[str]
    history: List[dict]
    completed: bool


class PracticeSessionStoreResponse(BaseModel):
    has_sessions: bool
    total_sessions: int
    latest_session_id: Optional[str]
    latest_summary: Optional[PracticeSessionSummaryResponse]


class AnswerScoringRequest(BaseModel):
    question: str
    answer: str
    job_description: Optional[str] = None


class AnswerScoringResponse(BaseModel):
    score: float
    strengths: List[str]
    improvements: List[str]
    improved_answer: str
