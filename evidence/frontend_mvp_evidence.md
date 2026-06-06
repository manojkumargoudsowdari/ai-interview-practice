# Frontend MVP Evidence

## 1. Git Branch Name

`feature/frontend-mvp`

## 2. Files Created/Modified

Modified:

- `.gitignore`
- `README.md`

Created under `frontend/`:

- `frontend/.gitignore`
- `frontend/README.md`
- `frontend/eslint.config.js`
- `frontend/index.html`
- `frontend/package-lock.json`
- `frontend/package.json`
- `frontend/public/favicon.svg`
- `frontend/public/icons.svg`
- `frontend/src/App.css`
- `frontend/src/App.tsx`
- `frontend/src/assets/hero.png`
- `frontend/src/assets/react.svg`
- `frontend/src/assets/vite.svg`
- `frontend/src/index.css`
- `frontend/src/main.tsx`
- `frontend/tsconfig.app.json`
- `frontend/tsconfig.json`
- `frontend/tsconfig.node.json`
- `frontend/vite.config.ts`

Created under `evidence/`:

- `evidence/frontend_mvp_evidence.md`
- `evidence/api_test_commands.md`
- `evidence/frontend_manual_test_checklist.md`

## 3. Commands Run

```powershell
git status --short --branch
git branch --show-current
git remote -v
node --version
npm --version
git checkout main
git checkout -b feature/frontend-mvp
npm create vite@latest frontend -- --template react-ts
npm install
npm run build
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/'
npm run dev -- --host 127.0.0.1
Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -UseBasicParsing
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/detect-question' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/generate-cues' -Method Post
Invoke-RestMethod -Uri 'http://127.0.0.1:8000/score-answer' -Method Post
npm run lint
npm run build
git status --short
```

## 4. Test Results

- Backend health check passed:

```json
{"app":"AI Interview Practice App","env":"local","status":"running"}
```

- Frontend dev server check passed:

```text
GET http://127.0.0.1:5173 returned HTTP 200
```

- `POST /detect-question` passed with a Databricks sample question.
- `POST /generate-cues` passed with the Spark optimization sample question.
- `POST /score-answer` passed with a short Spark optimization practice answer.
- `npm run build` passed.
- `npm run lint` initially found two caught-error preservation issues in `src/App.tsx`; after preserving the error cause, `npm run lint` passed.

## 5. API Endpoints Used By Frontend

- `GET http://127.0.0.1:8000/`
- `POST http://127.0.0.1:8000/detect-question`
- `POST http://127.0.0.1:8000/generate-cues`
- `POST http://127.0.0.1:8000/score-answer`

## 6. Screenshot Instructions

Actual screenshots were not captured in this run. To capture manual evidence:

1. Start the backend at `http://127.0.0.1:8000`.
2. Start the frontend with `npm run dev` from `frontend/`.
3. Open `http://localhost:5173`.
4. Take screenshots after each successful action:
   - Backend Health after clicking `Check Backend`
   - Question Detection after clicking `Detect Question`
   - Cue Generation after clicking `Generate Cues`
   - Answer Scoring after clicking `Score Answer`
5. Stop the backend and click any action button to capture backend-down error handling.

## 7. Known Issues

- Frontend API base URL is currently hard-coded to `http://127.0.0.1:8000`.
- Docker Compose is configured for the backend only. The frontend currently runs with Vite during development.
- Docker Desktop Linux engine may need to be started before Docker backend builds can run.
- No browser screenshots were captured automatically; manual screenshot instructions are listed above.

## 8. Next Recommended Step

Manually test the visible UI at `http://localhost:5173`, then add the next frontend feature: browser microphone recording or resume/JD upload, depending on the next practice workflow priority.
