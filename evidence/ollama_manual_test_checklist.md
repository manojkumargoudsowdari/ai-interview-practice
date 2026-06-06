# Ollama Manual Test Checklist

- [ ] Ollama installed
- [ ] Ollama API reachable
- [ ] `llama3.1:8b` model pulled or lighter model configured
- [ ] Backend `.env` switched to `ollama`
- [ ] Backend restarted
- [ ] `/llm/health` shows provider `ollama`
- [ ] `/llm/health` available `true`
- [ ] `/generate-cues` returns provider `ollama` or fallback provider if unavailable
- [ ] Frontend LLM status displays provider/model
- [ ] Frontend cue generation displays provider/risk flags/follow-up questions
- [ ] Mock provider still works after switching back
- [ ] Backend compile passes
- [ ] Frontend build passes
- [ ] Frontend lint passes
