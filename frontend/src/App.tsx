import { useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

type BackendHealth = {
  app: string
  env: string
  status: string
}

type QuestionDetectionResponse = {
  is_question: boolean
  question: string | null
  category: string | null
  topic: string | null
}

type CueGenerationResponse = {
  question: string
  cue_points: string[]
  short_direction: string
}

type AnswerScoringResponse = {
  score: number
  strengths: string[]
  improvements: string[]
  improved_answer: string
}

async function apiRequest<T>(path: string, options?: RequestInit): Promise<T> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
      ...options,
    })

    if (!response.ok) {
      throw new Error(`Backend returned ${response.status} ${response.statusText}`)
    }

    return (await response.json()) as T
  } catch (error) {
    if (error instanceof Error) {
      throw new Error(
        `Could not reach the backend at ${API_BASE_URL}. Make sure FastAPI is running. Details: ${error.message}`,
        { cause: error },
      )
    }

    throw new Error(`Could not reach the backend at ${API_BASE_URL}.`, { cause: error })
  }
}

function App() {
  const [health, setHealth] = useState<BackendHealth | null>(null)
  const [healthError, setHealthError] = useState('')
  const [healthLoading, setHealthLoading] = useState(false)

  const [transcript, setTranscript] = useState('How did you optimize Spark jobs?')
  const [detectedQuestion, setDetectedQuestion] = useState<QuestionDetectionResponse | null>(null)
  const [detectError, setDetectError] = useState('')
  const [detectLoading, setDetectLoading] = useState(false)

  const [cueQuestion, setCueQuestion] = useState('How did you optimize Spark jobs?')
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

    try {
      setCues(
        await apiRequest<CueGenerationResponse>('/generate-cues', {
          method: 'POST',
          body: JSON.stringify({
            question: cueQuestion,
            resume_context: cueResumeContext,
            job_description: cueJobDescription,
          }),
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

        <div className="form-grid">
          <label>
            Question
            <textarea value={cueQuestion} onChange={(event) => setCueQuestion(event.target.value)} rows={3} />
          </label>
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

        {cueError && <p className="error-message">{cueError}</p>}

        {cues && (
          <div className="result-block">
            <div className="chip-row">
              {cues.cue_points.map((cuePoint) => (
                <span className="chip" key={cuePoint}>
                  {cuePoint}
                </span>
              ))}
            </div>
            <p className="direction">{cues.short_direction}</p>
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
