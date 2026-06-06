# LLM Manual Test Checklist

Use this checklist with the backend running at `http://127.0.0.1:8000` and the frontend running at `http://localhost:5173`.

- [ ] Backend starts with `LLM_PROVIDER=mock`
- [ ] `/llm/health` works in mock mode
- [ ] `/generate-cues` works in mock mode
- [ ] Frontend shows provider
- [ ] Frontend shows risk flags and follow-up questions when returned by backend
- [ ] Backend starts with `LLM_PROVIDER=ollama`
- [ ] `/llm/health` works in ollama mode
- [ ] `/generate-cues` works in ollama mode
- [ ] Fallback works when Ollama is unavailable
- [ ] Frontend build passes with `npm run build`
- [ ] Frontend lint passes with `npm run lint`

## Ollama Manual Test Notes

Install and start Ollama, then run:

```powershell
ollama pull llama3.1:8b
```

Set `LLM_PROVIDER=ollama` in `backend/.env`, restart the backend, click `Check LLM Provider`, and generate cues from the frontend.
