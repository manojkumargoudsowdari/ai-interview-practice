import { useRef, useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

type BrowserSpeechRecognitionEvent = {
  resultIndex: number
  results: ArrayLike<{
    isFinal: boolean
    0: {
      transcript: string
    }
  }>
}

type BrowserSpeechRecognition = {
  continuous: boolean
  interimResults: boolean
  lang: string
  start: () => void
  stop: () => void
  onstart: (() => void) | null
  onend: (() => void) | null
  onerror: ((event: { error: string }) => void) | null
  onresult: ((event: BrowserSpeechRecognitionEvent) => void) | null
}

declare global {
  interface Window {
    SpeechRecognition?: new () => BrowserSpeechRecognition
    webkitSpeechRecognition?: new () => BrowserSpeechRecognition
  }
}

type BackendHealth = {
  app: string
  env: string
  status: string
}

type LLMHealthResponse = {
  provider: string
  configured: boolean
  available: boolean
  message: string
  ollama_base_url?: string | null
  ollama_model?: string | null
}

type QuestionDetectionResponse = {
  is_question: boolean
  question: string | null
  category: string | null
  topic: string | null
}

type UploadedDocumentResponse = {
  status: string
  filename: string | null
  source: string
  character_count: number
  preview: string
}

type PracticeContextResponse = {
  has_resume: boolean
  has_job_description: boolean
  resume_filename: string | null
  job_description_filename: string | null
  resume_char_count: number
  job_description_char_count: number
  updated_at: string | null
  resume_preview: string
  job_description_preview: string
}

type QuestionBankItem = {
  id: string
  category: string
  difficulty: string
  question: string
  interviewer_intent: string
  expected_answer_angle: string
  follow_up_questions: string[]
}

type QuestionBankGenerateResponse = {
  provider: string
  total_questions: number
  categories: string[]
  questions: QuestionBankItem[]
  warnings: string[]
}

type QuestionBankStoreResponse = {
  has_question_bank: boolean
  total_questions: number
  updated_at: string | null
  preview: QuestionBankItem[]
}

type CueGenerationResponse = {
  question: string
  cue_points: string[]
  short_direction: string
  risk_flags: string[]
  follow_up_questions: string[]
  provider: string
}

type AnswerScoringResponse = {
  score: number
  strengths: string[]
  improvements: string[]
  improved_answer: string
}

type PracticeSessionQuestion = {
  id: string
  category: string
  difficulty: string
  question: string
  interviewer_intent: string
  expected_answer_angle: string
  follow_up_questions: string[]
}

type PracticeSessionStartResponse = {
  session_id: string
  total_questions: number
  current_index: number
  current_question: PracticeSessionQuestion | null
  message: string
}

type PracticeAnswerScore = {
  score: number
  strengths: string[]
  improvements: string[]
  improved_answer: string
}

type PracticeAnswerSubmitResponse = {
  session_id: string
  question_id: string
  score: PracticeAnswerScore
  next_question: PracticeSessionQuestion | null
  completed: boolean
  progress: string
}

type PracticeAnswerGenerateResponse = {
  provider: string
  answer: string
  warnings: string[]
}

type VoicePracticeResponse = {
  transcript: string
  detection: QuestionDetectionResponse
  generated_answer: PracticeAnswerGenerateResponse | null
  message: string
}

type PracticeSessionSummaryResponse = {
  session_id: string
  total_questions: number
  answered_questions: number
  average_score: number | null
  weak_categories: string[]
  strong_categories: string[]
  history: Array<Record<string, unknown>>
  completed: boolean
}

type PracticeSessionStoreResponse = {
  has_sessions: boolean
  total_sessions: number
  latest_session_id: string | null
  latest_summary: PracticeSessionSummaryResponse | null
}

const QUESTION_CATEGORIES = [
  'all',
  'Resume walkthrough',
  'Project deep dive',
  'Spark / PySpark',
  'Databricks / Delta Lake',
  'ETL / pipelines',
  'Production support',
  'Data modeling',
  'AI-ready datasets',
  'RAG / AI agents',
  'Behavioral',
  'Pressure follow-ups',
]

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  const headers = new Headers(options?.headers)

  if (!(options?.body instanceof FormData) && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  let response: Response

  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers,
    })
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(
        `Could not reach the backend at ${API_BASE_URL}. Make sure FastAPI is running. Details: ${error.message}`,
        { cause: error },
      )
    }

    throw new Error(`Could not reach the backend at ${API_BASE_URL}.`, { cause: error })
  }

  if (!response.ok) {
    const detail = await readErrorDetail(response)
    throw new Error(detail || `Backend returned ${response.status} ${response.statusText}`)
  }

  return (await response.json()) as T
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const body = (await response.json()) as { detail?: string }
    return body.detail ?? ''
  } catch {
    return ''
  }
}

function App() {
  const speechRecognitionRef = useRef<BrowserSpeechRecognition | null>(null)

  const [health, setHealth] = useState<BackendHealth | null>(null)
  const [healthError, setHealthError] = useState('')
  const [healthLoading, setHealthLoading] = useState(false)

  const [llmHealth, setLlmHealth] = useState<LLMHealthResponse | null>(null)
  const [llmHealthError, setLlmHealthError] = useState('')
  const [llmHealthLoading, setLlmHealthLoading] = useState(false)

  const [resumeFile, setResumeFile] = useState<File | null>(null)
  const [resumeUpload, setResumeUpload] = useState<UploadedDocumentResponse | null>(null)
  const [resumeError, setResumeError] = useState('')
  const [resumeLoading, setResumeLoading] = useState(false)

  const [jdText, setJdText] = useState(
    'Senior data engineer role focused on Spark, Databricks, production pipelines, data quality, and Azure.',
  )
  const [jdFile, setJdFile] = useState<File | null>(null)
  const [jdUpload, setJdUpload] = useState<UploadedDocumentResponse | null>(null)
  const [jdError, setJdError] = useState('')
  const [jdLoading, setJdLoading] = useState(false)

  const [context, setContext] = useState<PracticeContextResponse | null>(null)
  const [contextError, setContextError] = useState('')
  const [contextLoading, setContextLoading] = useState(false)

  const [questionBankTotal, setQuestionBankTotal] = useState(55)
  const [questionBankDifficulty, setQuestionBankDifficulty] = useState('mixed')
  const [questionBankUseSavedContext, setQuestionBankUseSavedContext] = useState(true)
  const [questionBank, setQuestionBank] = useState<QuestionBankGenerateResponse | null>(null)
  const [questionBankStore, setQuestionBankStore] = useState<QuestionBankStoreResponse | null>(null)
  const [questionBankError, setQuestionBankError] = useState('')
  const [questionBankLoading, setQuestionBankLoading] = useState(false)

  const [practiceCategory, setPracticeCategory] = useState('all')
  const [practiceDifficulty, setPracticeDifficulty] = useState('mixed')
  const [practiceMaxQuestions, setPracticeMaxQuestions] = useState(10)
  const [practiceShuffle, setPracticeShuffle] = useState(true)
  const [practiceSessionId, setPracticeSessionId] = useState('')
  const [practiceCurrentQuestion, setPracticeCurrentQuestion] = useState<PracticeSessionQuestion | null>(null)
  const [practiceTotalQuestions, setPracticeTotalQuestions] = useState(0)
  const [practiceAnswer, setPracticeAnswer] = useState('')
  const [practiceGeneratedAnswer, setPracticeGeneratedAnswer] = useState<PracticeAnswerGenerateResponse | null>(null)
  const [practiceAnswerGenerating, setPracticeAnswerGenerating] = useState(false)
  const [practiceAnswerGenerateError, setPracticeAnswerGenerateError] = useState('')
  const [practiceScore, setPracticeScore] = useState<PracticeAnswerSubmitResponse | null>(null)
  const [practiceSummary, setPracticeSummary] = useState<PracticeSessionSummaryResponse | null>(null)
  const [practiceStore, setPracticeStore] = useState<PracticeSessionStoreResponse | null>(null)
  const [practiceError, setPracticeError] = useState('')
  const [practiceLoading, setPracticeLoading] = useState(false)

  const [transcript, setTranscript] = useState('How did you optimize Spark jobs?')
  const [detectedQuestion, setDetectedQuestion] = useState<QuestionDetectionResponse | null>(null)
  const [detectError, setDetectError] = useState('')
  const [detectLoading, setDetectLoading] = useState(false)

  const [cueQuestion, setCueQuestion] = useState('How did you optimize Spark jobs?')
  const [useSavedContext, setUseSavedContext] = useState(true)
  const [cueResumeContext, setCueResumeContext] = useState('')
  const [cueJobDescription, setCueJobDescription] = useState('')
  const [cues, setCues] = useState<CueGenerationResponse | null>(null)
  const [cueError, setCueError] = useState('')
  const [cueLoading, setCueLoading] = useState(false)

  const [scoreQuestion, setScoreQuestion] = useState('How did you optimize Spark jobs?')
  const [candidateAnswer, setCandidateAnswer] = useState(
    'I reviewed Spark UI stages, found shuffle skew, adjusted partitioning, and optimized file sizes. The pipeline became more stable in production and reduced latency for downstream reporting.',
  )
  const [scoreJobDescription, setScoreJobDescription] = useState('')
  const [scoreResult, setScoreResult] = useState<AnswerScoringResponse | null>(null)
  const [scoreError, setScoreError] = useState('')
  const [scoreLoading, setScoreLoading] = useState(false)

  const [voiceTranscript, setVoiceTranscript] = useState('')
  const [voiceInterimTranscript, setVoiceInterimTranscript] = useState('')
  const [voiceDetection, setVoiceDetection] = useState<QuestionDetectionResponse | null>(null)
  const [voiceGeneratedAnswer, setVoiceGeneratedAnswer] = useState<PracticeAnswerGenerateResponse | null>(null)
  const [voiceUseSavedContext, setVoiceUseSavedContext] = useState(true)
  const [voiceError, setVoiceError] = useState('')
  const [voiceListening, setVoiceListening] = useState(false)
  const [voiceProcessing, setVoiceProcessing] = useState(false)

  async function checkBackend() {
    setHealthLoading(true)
    setHealthError('')

    try {
      setHealth(await apiRequest<BackendHealth>('/'))
    } catch (error) {
      setHealth(null)
      setHealthError(error instanceof Error ? error.message : 'Backend health check failed.')
    } finally {
      setHealthLoading(false)
    }
  }

  async function checkLLMProvider() {
    setLlmHealthLoading(true)
    setLlmHealthError('')

    try {
      setLlmHealth(await apiRequest<LLMHealthResponse>('/llm/health'))
    } catch (error) {
      setLlmHealth(null)
      setLlmHealthError(error instanceof Error ? error.message : 'LLM provider health check failed.')
    } finally {
      setLlmHealthLoading(false)
    }
  }

  function startVoiceCapture() {
    setVoiceError('')
    setVoiceDetection(null)
    setVoiceGeneratedAnswer(null)
    setVoiceInterimTranscript('')

    const SpeechRecognitionConstructor = window.SpeechRecognition ?? window.webkitSpeechRecognition
    if (!SpeechRecognitionConstructor) {
      setVoiceError('Speech recognition is not supported in this browser. Use Chrome or Edge on localhost.')
      return
    }

    const recognition = new SpeechRecognitionConstructor()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => setVoiceListening(true)
    recognition.onend = () => {
      setVoiceListening(false)
      setVoiceInterimTranscript('')
    }
    recognition.onerror = (event) => {
      setVoiceListening(false)
      setVoiceError(`Microphone transcription failed: ${event.error}`)
    }
    recognition.onresult = (event) => {
      let finalText = ''
      let interimText = ''

      for (let index = event.resultIndex; index < event.results.length; index += 1) {
        const result = event.results[index]
        const text = result[0].transcript

        if (result.isFinal) {
          finalText += `${text} `
        } else {
          interimText += text
        }
      }

      if (finalText.trim()) {
        setVoiceTranscript((current) => `${current} ${finalText}`.replace(/\s+/g, ' ').trim())
      }
      setVoiceInterimTranscript(interimText.trim())
    }

    speechRecognitionRef.current = recognition
    recognition.start()
  }

  function stopVoiceCapture() {
    speechRecognitionRef.current?.stop()
    speechRecognitionRef.current = null
    setVoiceListening(false)
  }

  async function processVoiceTranscript() {
    setVoiceProcessing(true)
    setVoiceError('')

    try {
      const cleanTranscript = voiceTranscript.trim()
      if (!cleanTranscript) {
        throw new Error('Record or type the interviewer question first.')
      }

      const result = await apiRequest<VoicePracticeResponse>('/voice-practice/process-transcript', {
        method: 'POST',
        body: JSON.stringify({
          transcript: cleanTranscript,
          use_saved_context: voiceUseSavedContext,
        }),
      })

      setVoiceDetection(result.detection)
      setVoiceGeneratedAnswer(result.generated_answer)
      setTranscript(result.transcript)
      setDetectedQuestion(result.detection)

      const question = result.detection.question ?? result.transcript
      setCueQuestion(question)
      setScoreQuestion(question)

      if (result.generated_answer) {
        setCandidateAnswer(result.generated_answer.answer)
      }
    } catch (error) {
      setVoiceDetection(null)
      setVoiceGeneratedAnswer(null)
      setVoiceError(error instanceof Error ? error.message : 'Voice question processing failed.')
    } finally {
      setVoiceProcessing(false)
    }
  }

  function clearVoicePractice() {
    stopVoiceCapture()
    setVoiceTranscript('')
    setVoiceInterimTranscript('')
    setVoiceDetection(null)
    setVoiceGeneratedAnswer(null)
    setVoiceError('')
  }

  async function uploadResume() {
    setResumeLoading(true)
    setResumeError('')

    try {
      if (!resumeFile) {
        throw new Error('Choose a resume file first.')
      }

      const formData = new FormData()
      formData.append('file', resumeFile)
      const result = await apiRequest<UploadedDocumentResponse>('/upload/resume', {
        method: 'POST',
        body: formData,
      })

      setResumeUpload(result)
      await refreshContext()
    } catch (error) {
      setResumeUpload(null)
      setResumeError(error instanceof Error ? error.message : 'Resume upload failed.')
    } finally {
      setResumeLoading(false)
    }
  }

  async function saveJobDescriptionText() {
    setJdLoading(true)
    setJdError('')

    try {
      const result = await apiRequest<UploadedDocumentResponse>('/upload/job-description-text', {
        method: 'POST',
        body: JSON.stringify({ text: jdText, source: 'pasted_job_description' }),
      })

      setJdUpload(result)
      await refreshContext()
    } catch (error) {
      setJdUpload(null)
      setJdError(error instanceof Error ? error.message : 'Job description save failed.')
    } finally {
      setJdLoading(false)
    }
  }

  async function uploadJobDescriptionFile() {
    setJdLoading(true)
    setJdError('')

    try {
      if (!jdFile) {
        throw new Error('Choose a job description file first.')
      }

      const formData = new FormData()
      formData.append('file', jdFile)
      const result = await apiRequest<UploadedDocumentResponse>('/upload/job-description-file', {
        method: 'POST',
        body: formData,
      })

      setJdUpload(result)
      await refreshContext()
    } catch (error) {
      setJdUpload(null)
      setJdError(error instanceof Error ? error.message : 'Job description file upload failed.')
    } finally {
      setJdLoading(false)
    }
  }

  async function refreshContext() {
    setContextLoading(true)
    setContextError('')

    try {
      setContext(await apiRequest<PracticeContextResponse>('/context'))
    } catch (error) {
      setContext(null)
      setContextError(error instanceof Error ? error.message : 'Context refresh failed.')
    } finally {
      setContextLoading(false)
    }
  }

  async function clearSavedContext() {
    setContextLoading(true)
    setContextError('')

    try {
      await apiRequest<{ status: string }>('/context', { method: 'DELETE' })
      setContext(await apiRequest<PracticeContextResponse>('/context'))
      setResumeUpload(null)
      setJdUpload(null)
    } catch (error) {
      setContextError(error instanceof Error ? error.message : 'Context clear failed.')
    } finally {
      setContextLoading(false)
    }
  }

  async function generateQuestionBank() {
    setQuestionBankLoading(true)
    setQuestionBankError('')

    try {
      const result = await apiRequest<QuestionBankGenerateResponse>('/question-bank/generate', {
        method: 'POST',
        body: JSON.stringify({
          total_questions: questionBankTotal,
          difficulty: questionBankDifficulty,
          use_saved_context: questionBankUseSavedContext,
        }),
      })
      setQuestionBank(result)
      setQuestionBankStore(null)
    } catch (error) {
      setQuestionBank(null)
      setQuestionBankError(error instanceof Error ? error.message : 'Question bank generation failed.')
    } finally {
      setQuestionBankLoading(false)
    }
  }

  async function loadSavedQuestionBank() {
    setQuestionBankLoading(true)
    setQuestionBankError('')

    try {
      const result = await apiRequest<QuestionBankStoreResponse>('/question-bank')
      setQuestionBankStore(result)
      if (!result.has_question_bank) {
        setQuestionBank(null)
      }
    } catch (error) {
      setQuestionBankStore(null)
      setQuestionBankError(error instanceof Error ? error.message : 'Question bank load failed.')
    } finally {
      setQuestionBankLoading(false)
    }
  }

  async function clearSavedQuestionBank() {
    setQuestionBankLoading(true)
    setQuestionBankError('')

    try {
      await apiRequest<{ status: string }>('/question-bank', { method: 'DELETE' })
      setQuestionBank(null)
      setQuestionBankStore(await apiRequest<QuestionBankStoreResponse>('/question-bank'))
    } catch (error) {
      setQuestionBankError(error instanceof Error ? error.message : 'Question bank clear failed.')
    } finally {
      setQuestionBankLoading(false)
    }
  }

  async function startPracticeSession() {
    setPracticeLoading(true)
    setPracticeError('')

    try {
      const result = await apiRequest<PracticeSessionStartResponse>('/practice/start', {
        method: 'POST',
        body: JSON.stringify({
          category_filter: practiceCategory,
          difficulty_filter: practiceDifficulty,
          max_questions: practiceMaxQuestions,
          shuffle: practiceShuffle,
        }),
      })
      setPracticeSessionId(result.session_id)
      setPracticeCurrentQuestion(result.current_question)
      setPracticeTotalQuestions(result.total_questions)
      setPracticeAnswer('')
      setPracticeGeneratedAnswer(null)
      setPracticeAnswerGenerateError('')
      setPracticeScore(null)
      setPracticeSummary(null)
      setPracticeStore(null)
    } catch (error) {
      setPracticeError(error instanceof Error ? error.message : 'Practice session start failed.')
    } finally {
      setPracticeLoading(false)
    }
  }

  async function generatePracticeAnswer() {
    setPracticeAnswerGenerating(true)
    setPracticeAnswerGenerateError('')

    try {
      if (!practiceCurrentQuestion) {
        throw new Error('Start a practice session and load a question first.')
      }

      const result = await apiRequest<PracticeAnswerGenerateResponse>('/practice/generate-answer', {
        method: 'POST',
        body: JSON.stringify({
          question: practiceCurrentQuestion.question,
          category: practiceCurrentQuestion.category,
          difficulty: practiceCurrentQuestion.difficulty,
          interviewer_intent: practiceCurrentQuestion.interviewer_intent,
          expected_answer_angle: practiceCurrentQuestion.expected_answer_angle,
          follow_up_questions: practiceCurrentQuestion.follow_up_questions,
          use_saved_context: true,
        }),
      })

      setPracticeGeneratedAnswer(result)
      setPracticeAnswer(result.answer)
    } catch (error) {
      setPracticeGeneratedAnswer(null)
      setPracticeAnswerGenerateError(error instanceof Error ? error.message : 'Practice answer generation failed.')
    } finally {
      setPracticeAnswerGenerating(false)
    }
  }

  async function submitPracticeAnswer() {
    setPracticeLoading(true)
    setPracticeError('')

    try {
      if (!practiceSessionId || !practiceCurrentQuestion) {
        throw new Error('Start a practice session first.')
      }

      const result = await apiRequest<PracticeAnswerSubmitResponse>('/practice/answer', {
        method: 'POST',
        body: JSON.stringify({
          session_id: practiceSessionId,
          question_id: practiceCurrentQuestion.id,
          answer: practiceAnswer,
        }),
      })
      setPracticeScore(result)
      setPracticeCurrentQuestion(result.next_question)
      setPracticeAnswer('')
      setPracticeGeneratedAnswer(null)
      setPracticeAnswerGenerateError('')

      if (result.completed) {
        setPracticeSummary(await apiRequest<PracticeSessionSummaryResponse>(`/practice/session/${practiceSessionId}`))
      }
    } catch (error) {
      setPracticeError(error instanceof Error ? error.message : 'Practice answer submit failed.')
    } finally {
      setPracticeLoading(false)
    }
  }

  async function loadLatestPracticeSession() {
    setPracticeLoading(true)
    setPracticeError('')

    try {
      const result = await apiRequest<PracticeSessionStoreResponse>('/practice/sessions')
      setPracticeStore(result)
      setPracticeSummary(result.latest_summary)
      setPracticeSessionId(result.latest_session_id ?? '')
      setPracticeCurrentQuestion(null)
      setPracticeGeneratedAnswer(null)
      setPracticeAnswerGenerateError('')
      setPracticeScore(null)
    } catch (error) {
      setPracticeStore(null)
      setPracticeError(error instanceof Error ? error.message : 'Practice session load failed.')
    } finally {
      setPracticeLoading(false)
    }
  }

  async function clearPracticeSessions() {
    setPracticeLoading(true)
    setPracticeError('')

    try {
      await apiRequest<{ status: string }>('/practice/sessions', { method: 'DELETE' })
      setPracticeSessionId('')
      setPracticeCurrentQuestion(null)
      setPracticeTotalQuestions(0)
      setPracticeAnswer('')
      setPracticeGeneratedAnswer(null)
      setPracticeAnswerGenerateError('')
      setPracticeScore(null)
      setPracticeSummary(null)
      setPracticeStore(await apiRequest<PracticeSessionStoreResponse>('/practice/sessions'))
    } catch (error) {
      setPracticeError(error instanceof Error ? error.message : 'Practice sessions clear failed.')
    } finally {
      setPracticeLoading(false)
    }
  }

  async function detectQuestion() {
    setDetectLoading(true)
    setDetectError('')

    try {
      setDetectedQuestion(
        await apiRequest<QuestionDetectionResponse>('/detect-question', {
          method: 'POST',
          body: JSON.stringify({ transcript }),
        }),
      )
    } catch (error) {
      setDetectedQuestion(null)
      setDetectError(error instanceof Error ? error.message : 'Question detection failed.')
    } finally {
      setDetectLoading(false)
    }
  }

  async function generateCues() {
    setCueLoading(true)
    setCueError('')

    const body = useSavedContext
      ? { question: cueQuestion }
      : {
          question: cueQuestion,
          resume_context: cueResumeContext,
          job_description: cueJobDescription,
        }

    try {
      setCues(
        await apiRequest<CueGenerationResponse>('/generate-cues', {
          method: 'POST',
          body: JSON.stringify(body),
        }),
      )
    } catch (error) {
      setCues(null)
      setCueError(error instanceof Error ? error.message : 'Cue generation failed.')
    } finally {
      setCueLoading(false)
    }
  }

  async function scoreAnswer() {
    setScoreLoading(true)
    setScoreError('')

    try {
      setScoreResult(
        await apiRequest<AnswerScoringResponse>('/score-answer', {
          method: 'POST',
          body: JSON.stringify({
            question: scoreQuestion,
            answer: candidateAnswer,
            job_description: scoreJobDescription,
          }),
        }),
      )
    } catch (error) {
      setScoreResult(null)
      setScoreError(error instanceof Error ? error.message : 'Answer scoring failed.')
    } finally {
      setScoreLoading(false)
    }
  }

  return (
    <main className="app-shell">
      <header className="app-header">
        <div>
          <p className="eyebrow">Practice workspace</p>
          <h1>AI Interview Practice App</h1>
        </div>
        <a className="docs-link" href={`${API_BASE_URL}/docs`} target="_blank" rel="noreferrer">
          API Docs
        </a>
      </header>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Backend Health</h2>
            <p>Confirm the FastAPI service is reachable before testing workflows.</p>
          </div>
          <button type="button" onClick={checkBackend} disabled={healthLoading}>
            {healthLoading ? 'Checking...' : 'Check Backend'}
          </button>
        </div>

        {healthError && <p className="error-message">{healthError}</p>}

        {health && (
          <dl className="result-grid">
            <div>
              <dt>App</dt>
              <dd>{health.app}</dd>
            </div>
            <div>
              <dt>Environment</dt>
              <dd>{health.env}</dd>
            </div>
            <div>
              <dt>Status</dt>
              <dd>{health.status}</dd>
            </div>
          </dl>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Live Audio Question</h2>
            <p>Capture a spoken interviewer question, detect it, and generate a practice answer.</p>
          </div>
          <div className="button-row">
            <button type="button" onClick={startVoiceCapture} disabled={voiceListening}>
              {voiceListening ? 'Listening...' : 'Start Listening'}
            </button>
            <button type="button" onClick={stopVoiceCapture} disabled={!voiceListening}>
              Stop
            </button>
            <button type="button" onClick={processVoiceTranscript} disabled={voiceProcessing || voiceListening}>
              {voiceProcessing ? 'Generating...' : 'Generate Answer'}
            </button>
            <button className="danger-button" type="button" onClick={clearVoicePractice}>
              Clear
            </button>
          </div>
        </div>

        <label className="checkbox-row">
          <input
            checked={voiceUseSavedContext}
            type="checkbox"
            onChange={(event) => setVoiceUseSavedContext(event.target.checked)}
          />
          Use saved resume/JD context
        </label>

        <label>
          Captured question transcript
          <textarea
            value={voiceTranscript}
            onChange={(event) => setVoiceTranscript(event.target.value)}
            rows={4}
            placeholder="Click Start Listening, ask the question, then click Stop."
          />
        </label>

        {voiceInterimTranscript && (
          <p className="listening-text">
            Listening: {voiceInterimTranscript}
          </p>
        )}

        {voiceError && <p className="error-message">{voiceError}</p>}

        {voiceDetection && (
          <dl className="result-grid">
            <div>
              <dt>is_question</dt>
              <dd>{String(voiceDetection.is_question)}</dd>
            </div>
            <div>
              <dt>question</dt>
              <dd>{voiceDetection.question ?? 'None'}</dd>
            </div>
            <div>
              <dt>category</dt>
              <dd>{voiceDetection.category ?? 'None'}</dd>
            </div>
            <div>
              <dt>topic</dt>
              <dd>{voiceDetection.topic ?? 'None'}</dd>
            </div>
          </dl>
        )}

        {voiceGeneratedAnswer && (
          <div className="generated-answer">
            <dl className="compact-meta">
              <div>
                <dt>Provider</dt>
                <dd>{voiceGeneratedAnswer.provider}</dd>
              </div>
            </dl>
            <h3>Generated answer to read aloud</h3>
            <p>{voiceGeneratedAnswer.answer}</p>
            <CueList title="Warnings" items={voiceGeneratedAnswer.warnings} tone="risk" />
          </div>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Practice Session</h2>
            <p>Practice saved question-bank questions one at a time and save scored answer history.</p>
          </div>
          <div className="button-row">
            <button type="button" onClick={startPracticeSession} disabled={practiceLoading}>
              {practiceLoading ? 'Starting...' : 'Start Practice Session'}
            </button>
            <button type="button" onClick={loadLatestPracticeSession} disabled={practiceLoading}>
              Load Latest Session
            </button>
            <button className="danger-button" type="button" onClick={clearPracticeSessions} disabled={practiceLoading}>
              Clear Practice Sessions
            </button>
          </div>
        </div>

        <div className="practice-controls">
          <label>
            Category
            <select value={practiceCategory} onChange={(event) => setPracticeCategory(event.target.value)}>
              {QUESTION_CATEGORIES.map((category) => (
                <option key={category} value={category}>
                  {category}
                </option>
              ))}
            </select>
          </label>
          <label>
            Difficulty
            <select value={practiceDifficulty} onChange={(event) => setPracticeDifficulty(event.target.value)}>
              <option value="mixed">mixed</option>
              <option value="easy">easy</option>
              <option value="medium">medium</option>
              <option value="hard">hard</option>
            </select>
          </label>
          <label>
            Max questions
            <input
              min={1}
              max={50}
              type="number"
              value={practiceMaxQuestions}
              onChange={(event) => setPracticeMaxQuestions(Number(event.target.value))}
            />
          </label>
          <label className="checkbox-row">
            <input checked={practiceShuffle} type="checkbox" onChange={(event) => setPracticeShuffle(event.target.checked)} />
            Shuffle questions
          </label>
        </div>

        {practiceError && <p className="error-message">{practiceError}</p>}

        {practiceStore && (
          <dl className="result-grid">
            <div>
              <dt>Saved sessions</dt>
              <dd>{practiceStore.has_sessions ? 'Yes' : 'No'}</dd>
            </div>
            <div>
              <dt>Total sessions</dt>
              <dd>{practiceStore.total_sessions}</dd>
            </div>
            <div>
              <dt>Latest session</dt>
              <dd>{practiceStore.latest_session_id ?? 'None'}</dd>
            </div>
          </dl>
        )}

        {practiceCurrentQuestion && (
          <div className="practice-session-layout">
            <PracticeQuestionCard question={practiceCurrentQuestion} />
            <div className="practice-answer-tools">
              <button type="button" onClick={generatePracticeAnswer} disabled={practiceAnswerGenerating || practiceLoading}>
                {practiceAnswerGenerating ? 'Generating...' : 'Generate Answer'}
              </button>
              <p className="helper-text">
                Generates a safe read-aloud draft from the current question and saved resume/JD context.
              </p>
            </div>
            {practiceAnswerGenerateError && <p className="error-message">{practiceAnswerGenerateError}</p>}
            {practiceGeneratedAnswer && (
              <div className="generated-answer">
                <dl className="compact-meta">
                  <div>
                    <dt>Provider</dt>
                    <dd>{practiceGeneratedAnswer.provider}</dd>
                  </div>
                </dl>
                <h3>Generated practice answer</h3>
                <p>{practiceGeneratedAnswer.answer}</p>
                <CueList title="Warnings" items={practiceGeneratedAnswer.warnings} tone="risk" />
              </div>
            )}
            <label>
              My answer
              <textarea value={practiceAnswer} onChange={(event) => setPracticeAnswer(event.target.value)} rows={6} />
            </label>
            <button type="button" onClick={submitPracticeAnswer} disabled={practiceLoading}>
              {practiceLoading ? 'Scoring...' : 'Submit Answer'}
            </button>
            <p className="helper-text">
              Session {practiceSessionId} · {practiceTotalQuestions} questions
            </p>
          </div>
        )}

        {practiceScore && (
          <div className="score-layout">
            <div className="score-card">
              <span className="score-value">{practiceScore.score.score.toFixed(1)}</span>
              <span className="score-label">Score</span>
            </div>
            <div className="feedback-columns">
              <FeedbackList title="Strengths" items={practiceScore.score.strengths} />
              <FeedbackList title="Improvements" items={practiceScore.score.improvements} />
            </div>
            <div className="guidance">
              <h3>Improved answer guidance</h3>
              <p>{practiceScore.score.improved_answer}</p>
              <p className="helper-text">Progress: {practiceScore.progress}</p>
            </div>
          </div>
        )}

        {practiceSummary && (
          <PracticeSummary summary={practiceSummary} />
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Question Bank</h2>
            <p>Generate categorized practice questions from saved resume and job description context.</p>
          </div>
          <div className="button-row">
            <button type="button" onClick={generateQuestionBank} disabled={questionBankLoading}>
              {questionBankLoading ? 'Generating...' : 'Generate Question Bank'}
            </button>
            <button type="button" onClick={loadSavedQuestionBank} disabled={questionBankLoading}>
              Load Saved Question Bank
            </button>
            <button className="danger-button" type="button" onClick={clearSavedQuestionBank} disabled={questionBankLoading}>
              Clear Question Bank
            </button>
          </div>
        </div>

        <div className="question-bank-controls">
          <label>
            Total questions
            <input
              min={11}
              max={110}
              type="number"
              value={questionBankTotal}
              onChange={(event) => setQuestionBankTotal(Number(event.target.value))}
            />
          </label>
          <label>
            Difficulty
            <select value={questionBankDifficulty} onChange={(event) => setQuestionBankDifficulty(event.target.value)}>
              <option value="mixed">mixed</option>
              <option value="easy">easy</option>
              <option value="medium">medium</option>
              <option value="hard">hard</option>
            </select>
          </label>
          <label className="checkbox-row">
            <input
              checked={questionBankUseSavedContext}
              type="checkbox"
              onChange={(event) => setQuestionBankUseSavedContext(event.target.checked)}
            />
            Use saved resume/JD context
          </label>
        </div>

        {questionBankError && <p className="error-message">{questionBankError}</p>}

        {questionBankStore && (
          <div className="result-block">
            <dl className="compact-meta">
              <div>
                <dt>Saved</dt>
                <dd>{questionBankStore.has_question_bank ? 'Yes' : 'No'}</dd>
              </div>
              <div>
                <dt>Total</dt>
                <dd>{questionBankStore.total_questions}</dd>
              </div>
              <div>
                <dt>Updated</dt>
                <dd>{questionBankStore.updated_at ?? 'Never'}</dd>
              </div>
            </dl>
            {questionBankStore.preview.length > 0 && (
              <QuestionBankGroups questions={questionBankStore.preview} />
            )}
          </div>
        )}

        {questionBank && (
          <div className="result-block">
            <dl className="compact-meta">
              <div>
                <dt>Provider</dt>
                <dd>{questionBank.provider}</dd>
              </div>
              <div>
                <dt>Total</dt>
                <dd>{questionBank.total_questions}</dd>
              </div>
              <div>
                <dt>Categories</dt>
                <dd>{questionBank.categories.length}</dd>
              </div>
            </dl>
            {questionBank.warnings.length > 0 && (
              <CueList title="Warnings" items={questionBank.warnings} tone="risk" />
            )}
            <QuestionBankGroups questions={questionBank.questions} />
          </div>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>LLM Provider</h2>
            <p>Check whether cue generation is using mock mode or a local Ollama model.</p>
            <p className="helper-text">Use backend/.env to switch between mock and ollama providers.</p>
          </div>
          <button type="button" onClick={checkLLMProvider} disabled={llmHealthLoading}>
            {llmHealthLoading ? 'Checking...' : 'Check LLM Provider'}
          </button>
        </div>

        {llmHealthError && <p className="error-message">{llmHealthError}</p>}

        {llmHealth && (
          <dl className="result-grid">
            <div>
              <dt>Provider</dt>
              <dd>{llmHealth.provider}</dd>
            </div>
            <div>
              <dt>Configured</dt>
              <dd>{String(llmHealth.configured)}</dd>
            </div>
            <div>
              <dt>Available</dt>
              <dd>
                <span className={llmHealth.available ? 'status-pill is-ok' : 'status-pill is-warning'}>
                  {String(llmHealth.available)}
                </span>
              </dd>
            </div>
            <div>
              <dt>Model</dt>
              <dd>{llmHealth.ollama_model ?? 'Not applicable'}</dd>
            </div>
            <div>
              <dt>Message</dt>
              <dd>{llmHealth.message}</dd>
            </div>
          </dl>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Resume &amp; JD Context</h2>
            <p>Upload practice documents or paste a job description for saved cue context.</p>
          </div>
          <div className="button-row">
            <button type="button" onClick={refreshContext} disabled={contextLoading}>
              {contextLoading ? 'Refreshing...' : 'Refresh Context'}
            </button>
            <button className="danger-button" type="button" onClick={clearSavedContext} disabled={contextLoading}>
              Clear Context
            </button>
          </div>
        </div>

        <div className="context-layout">
          <div className="upload-block">
            <h3>Resume File</h3>
            <label>
              Upload resume file
              <input
                accept=".pdf,.txt,.md"
                type="file"
                onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <button type="button" onClick={uploadResume} disabled={resumeLoading}>
              {resumeLoading ? 'Uploading...' : 'Upload Resume'}
            </button>
            {resumeError && <p className="error-message">{resumeError}</p>}
            {resumeUpload && <UploadResult result={resumeUpload} />}
          </div>

          <div className="upload-block">
            <h3>Job Description</h3>
            <label>
              Paste JD text
              <textarea value={jdText} onChange={(event) => setJdText(event.target.value)} rows={5} />
            </label>
            <button type="button" onClick={saveJobDescriptionText} disabled={jdLoading}>
              {jdLoading ? 'Saving...' : 'Save JD Text'}
            </button>

            <label>
              Upload JD file optional
              <input
                accept=".pdf,.txt,.md"
                type="file"
                onChange={(event) => setJdFile(event.target.files?.[0] ?? null)}
              />
            </label>
            <button type="button" onClick={uploadJobDescriptionFile} disabled={jdLoading}>
              {jdLoading ? 'Uploading...' : 'Upload JD File'}
            </button>
            {jdError && <p className="error-message">{jdError}</p>}
            {jdUpload && <UploadResult result={jdUpload} />}
          </div>
        </div>

        {contextError && <p className="error-message">{contextError}</p>}

        {context && (
          <div className="context-panel">
            <h3>Current Context</h3>
            <dl className="result-grid">
              <div>
                <dt>Resume loaded</dt>
                <dd>{context.has_resume ? 'Yes' : 'No'}</dd>
              </div>
              <div>
                <dt>JD loaded</dt>
                <dd>{context.has_job_description ? 'Yes' : 'No'}</dd>
              </div>
              <div>
                <dt>Resume source</dt>
                <dd>{context.resume_filename ?? 'None'}</dd>
              </div>
              <div>
                <dt>JD source</dt>
                <dd>{context.job_description_filename ?? 'None'}</dd>
              </div>
              <div>
                <dt>Resume chars</dt>
                <dd>{context.resume_char_count}</dd>
              </div>
              <div>
                <dt>JD chars</dt>
                <dd>{context.job_description_char_count}</dd>
              </div>
              <div>
                <dt>Updated</dt>
                <dd>{context.updated_at ?? 'Never'}</dd>
              </div>
            </dl>
            <div className="preview-grid">
              <PreviewCard title="Resume preview" preview={context.resume_preview} />
              <PreviewCard title="JD preview" preview={context.job_description_preview} />
            </div>
          </div>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Question Detection</h2>
            <p>Paste an interviewer transcript and classify whether it contains a question.</p>
          </div>
          <button type="button" onClick={detectQuestion} disabled={detectLoading}>
            {detectLoading ? 'Detecting...' : 'Detect Question'}
          </button>
        </div>

        <label>
          Interviewer transcript/question
          <textarea value={transcript} onChange={(event) => setTranscript(event.target.value)} rows={4} />
        </label>

        {detectError && <p className="error-message">{detectError}</p>}

        {detectedQuestion && (
          <dl className="result-grid">
            <div>
              <dt>is_question</dt>
              <dd>{String(detectedQuestion.is_question)}</dd>
            </div>
            <div>
              <dt>question</dt>
              <dd>{detectedQuestion.question ?? 'None'}</dd>
            </div>
            <div>
              <dt>category</dt>
              <dd>{detectedQuestion.category ?? 'None'}</dd>
            </div>
            <div>
              <dt>topic</dt>
              <dd>{detectedQuestion.topic ?? 'None'}</dd>
            </div>
          </dl>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Cue Generation</h2>
            <p>Generate concise talking points for a practice answer.</p>
          </div>
          <button type="button" onClick={generateCues} disabled={cueLoading}>
            {cueLoading ? 'Generating...' : 'Generate Cues'}
          </button>
        </div>

        <label>
          Question
          <textarea value={cueQuestion} onChange={(event) => setCueQuestion(event.target.value)} rows={3} />
        </label>

        <label className="checkbox-row">
          <input
            checked={useSavedContext}
            type="checkbox"
            onChange={(event) => setUseSavedContext(event.target.checked)}
          />
          Use saved resume/JD context
        </label>

        {!useSavedContext && (
          <div className="form-grid">
            <label>
              Resume context optional
              <textarea
                value={cueResumeContext}
                onChange={(event) => setCueResumeContext(event.target.value)}
                rows={3}
              />
            </label>
            <label>
              Job description optional
              <textarea
                value={cueJobDescription}
                onChange={(event) => setCueJobDescription(event.target.value)}
                rows={3}
              />
            </label>
          </div>
        )}

        {cueError && <p className="error-message">{cueError}</p>}

        {cues && (
          <div className="result-block">
            <dl className="compact-meta">
              <div>
                <dt>Provider</dt>
                <dd>{cues.provider}</dd>
              </div>
            </dl>
            <div className="chip-row">
              {cues.cue_points.map((cuePoint) => (
                <span className="chip" key={cuePoint}>
                  {cuePoint}
                </span>
              ))}
            </div>
            <p className="direction">{cues.short_direction}</p>
            <CueList title="Risk flags" items={cues.risk_flags} tone="risk" />
            <CueList title="Follow-up questions" items={cues.follow_up_questions} />
          </div>
        )}
      </section>

      <section className="panel">
        <div className="section-heading">
          <div>
            <h2>Answer Scoring</h2>
            <p>Score a practice answer and get focused improvement guidance.</p>
          </div>
          <button type="button" onClick={scoreAnswer} disabled={scoreLoading}>
            {scoreLoading ? 'Scoring...' : 'Score Answer'}
          </button>
        </div>

        <div className="form-grid">
          <label>
            Question
            <textarea value={scoreQuestion} onChange={(event) => setScoreQuestion(event.target.value)} rows={3} />
          </label>
          <label>
            Candidate answer
            <textarea value={candidateAnswer} onChange={(event) => setCandidateAnswer(event.target.value)} rows={5} />
          </label>
          <label>
            Job description optional
            <textarea
              value={scoreJobDescription}
              onChange={(event) => setScoreJobDescription(event.target.value)}
              rows={3}
            />
          </label>
        </div>

        {scoreError && <p className="error-message">{scoreError}</p>}

        {scoreResult && (
          <div className="score-layout">
            <div className="score-card">
              <span className="score-value">{scoreResult.score.toFixed(1)}</span>
              <span className="score-label">Score</span>
            </div>
            <div className="feedback-columns">
              <FeedbackList title="Strengths" items={scoreResult.strengths} />
              <FeedbackList title="Improvements" items={scoreResult.improvements} />
            </div>
            <div className="guidance">
              <h3>Improved answer guidance</h3>
              <p>{scoreResult.improved_answer}</p>
            </div>
          </div>
        )}
      </section>
    </main>
  )
}

function CueList({ title, items, tone = 'default' }: { title: string; items: string[]; tone?: 'default' | 'risk' }) {
  if (!items.length) {
    return null
  }

  return (
    <div className={`cue-list ${tone === 'risk' ? 'cue-list-risk' : ''}`}>
      <h3>{title}</h3>
      <ul>
        {items.map((item) => (
          <li key={item}>{item}</li>
        ))}
      </ul>
    </div>
  )
}

function QuestionBankGroups({ questions }: { questions: QuestionBankItem[] }) {
  const groupedQuestions = questions.reduce<Record<string, QuestionBankItem[]>>((groups, question) => {
    groups[question.category] = groups[question.category] ?? []
    groups[question.category].push(question)
    return groups
  }, {})

  return (
    <div className="question-bank-groups">
      {Object.entries(groupedQuestions).map(([category, items]) => (
        <section className="question-category" key={category}>
          <h3>{category}</h3>
          <div className="question-card-list">
            {items.map((item) => (
              <article className="question-card" key={item.id}>
                <span className="difficulty-pill">{item.difficulty}</span>
                <h4>{item.question}</h4>
                <p>
                  <strong>Interviewer intent:</strong> {item.interviewer_intent}
                </p>
                <p>
                  <strong>Expected answer angle:</strong> {item.expected_answer_angle}
                </p>
                {item.follow_up_questions.length > 0 && (
                  <div>
                    <strong>Follow-ups</strong>
                    <ul>
                      {item.follow_up_questions.map((followUp) => (
                        <li key={followUp}>{followUp}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </article>
            ))}
          </div>
        </section>
      ))}
    </div>
  )
}

function PracticeQuestionCard({ question }: { question: PracticeSessionQuestion }) {
  return (
    <article className="question-card practice-question-card">
      <span className="difficulty-pill">{question.difficulty}</span>
      <h4>{question.question}</h4>
      <p>
        <strong>Category:</strong> {question.category}
      </p>
      <p>
        <strong>Interviewer intent:</strong> {question.interviewer_intent}
      </p>
      <p>
        <strong>Expected answer angle:</strong> {question.expected_answer_angle}
      </p>
      {question.follow_up_questions.length > 0 && (
        <div>
          <strong>Follow-ups</strong>
          <ul>
            {question.follow_up_questions.map((followUp) => (
              <li key={followUp}>{followUp}</li>
            ))}
          </ul>
        </div>
      )}
    </article>
  )
}

function PracticeSummary({ summary }: { summary: PracticeSessionSummaryResponse }) {
  return (
    <div className="result-block">
      <h3>Session Summary</h3>
      <dl className="result-grid">
        <div>
          <dt>Average score</dt>
          <dd>{summary.average_score ?? 'Not scored yet'}</dd>
        </div>
        <div>
          <dt>Answered</dt>
          <dd>
            {summary.answered_questions}/{summary.total_questions}
          </dd>
        </div>
        <div>
          <dt>Completed</dt>
          <dd>{String(summary.completed)}</dd>
        </div>
      </dl>
      <div className="feedback-columns">
        <FeedbackList title="Weak categories" items={summary.weak_categories} />
        <FeedbackList title="Strong categories" items={summary.strong_categories} />
      </div>
    </div>
  )
}

function UploadResult({ result }: { result: UploadedDocumentResponse }) {
  return (
    <div className="upload-result">
      <p>
        <strong>{result.filename ?? result.source}</strong> saved with {result.character_count} characters.
      </p>
      <p>{result.preview}</p>
    </div>
  )
}

function PreviewCard({ title, preview }: { title: string; preview: string }) {
  return (
    <div className="preview-card">
      <h3>{title}</h3>
      <p>{preview || 'No saved text yet.'}</p>
    </div>
  )
}

function FeedbackList({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3>{title}</h3>
      {items.length > 0 ? (
        <ul>
          {items.map((item) => (
            <li key={item}>{item}</li>
          ))}
        </ul>
      ) : (
        <p>No items returned.</p>
      )}
    </div>
  )
}

export default App
