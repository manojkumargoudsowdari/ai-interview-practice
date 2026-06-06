import { useState } from 'react'
import './App.css'

const API_BASE_URL = 'http://127.0.0.1:8000'

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
            <h2>LLM Provider</h2>
            <p>Check whether cue generation is using mock mode or a local Ollama model.</p>
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
