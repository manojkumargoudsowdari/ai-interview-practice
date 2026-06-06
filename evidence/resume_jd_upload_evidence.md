# Resume and JD Upload Evidence

## 1. Branch Name

`feature/resume-jd-upload`

## 2. Summary of Feature

Added local resume and job description context support for the visible AI Interview Practice App.

The backend can now extract text from `.txt`, `.md`, and `.pdf` uploads, save resume/JD context in a local JSON store, return context metadata, clear saved context, and use saved context as the fallback input for cue generation.

The frontend now includes a `Resume & JD Context` section for uploading a resume, pasting or uploading a job description, refreshing current context, clearing saved context, and generating cues with saved context.

## 3. Files Created/Modified

Modified:

- `.gitignore`
- `README.md`
- `backend/requirements.txt`
- `backend/app/main.py`
- `backend/app/schemas.py`
- `backend/app/services/cue_generator.py`
- `frontend/README.md`
- `frontend/src/App.css`
- `frontend/src/App.tsx`

Created:

- `backend/app/services/document_processor.py`
- `backend/app/services/context_store.py`
- `backend/data/uploads/.gitkeep`
- `backend/data/processed/.gitkeep`
- `evidence/resume_jd_upload_evidence.md`
- `evidence/upload_api_test_commands.md`
- `evidence/resume_jd_manual_test_checklist.md`
- `evidence/sample_inputs/sample_resume.txt`
- `evidence/sample_inputs/sample_job_description.txt`
- `evidence/sample_inputs/unsupported_file.json`

Ignored runtime/private files:

- `backend/data/uploads/*`
- `backend/data/processed/*`
- `backend/data/processed/context.json`

## 4. Backend Endpoints Added

- `POST /upload/resume`
- `POST /upload/job-description-file`
- `POST /upload/job-description-text`
- `GET /context`
- `DELETE /context`

Updated:

- `POST /generate-cues` now falls back to saved resume/JD context when manual `resume_context` or `job_description` values are not provided.

## 5. Frontend Sections Added

Added `Resume & JD Context` section with:

- Resume file upload for `.pdf`, `.txt`, `.md`
- JD pasted text save
- Optional JD file upload for `.pdf`, `.txt`, `.md`
- Current context panel with loaded flags, source filenames, character counts, updated timestamp, and previews
- Clear context button
- Cue generation checkbox: `Use saved resume/JD context`

## 6. Commands Run

```powershell
git status --short --branch
git branch --show-current
rg --files
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\python -m compileall app
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/context' -Method Delete
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/upload/resume' -Method Post -Form @{ file = Get-Item $resumePath }
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/upload/job-description-text' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/context'
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/generate-cues' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/upload/resume' -Method Post -Form @{ file = Get-Item $unsupportedPath }
npm run lint
npm run build
git status --short
git branch --show-current
```

## 7. Test Results

- Backend health check passed:

```json
{"app":"AI Interview Practice App","env":"local","status":"running"}
```

- Resume TXT upload passed with `evidence/sample_inputs/sample_resume.txt`.
- JD pasted text save passed with `evidence/sample_inputs/sample_job_description.txt`.
- `GET /context` passed and returned saved resume + JD metadata.
- `POST /generate-cues` using saved context passed and returned context-derived cue points including `Databricks`, `Azure`, and `senior ownership`.
- Unsupported `.json` upload failed cleanly with HTTP 400 and a supported-types message.
- `npm run lint` passed.
- `npm run build` passed.
- Backend Python compile check passed.

PDF support is implemented with `pypdf`, but automatic PDF extraction was not tested because no sample PDF exists in the project. Manual PDF test instructions are included in `evidence/resume_jd_manual_test_checklist.md`.

## 8. Known Issues

- Saved context is a local single-user JSON file, not a database.
- Uploaded source files are saved locally under `backend/data/uploads/` and ignored by Git.
- `backend/data/processed/context.json` is ignored by Git and should not be committed.
- Frontend API base URL remains hard-coded to `http://127.0.0.1:8000`.
- No automatic browser screenshot capture was run.
- PDF parsing quality depends on the PDF text layer. Scanned image-only PDFs will likely need OCR later.

## 9. Next Recommended Step

Add resume/JD preview editing or chunked retrieval so cue generation can use more targeted context instead of the current full saved text fallback.
