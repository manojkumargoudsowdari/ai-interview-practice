# Ollama Manual Test Checklist

- [ ] Ollama installed
- [ ] Ollama API reachable
- [ ] `llama3.2:3b` model pulled or larger model configured
- [ ] Set provider to mock using `.\scripts\set_llm_provider.ps1 -Provider mock`
- [ ] Set provider to ollama using `.\scripts\set_llm_provider.ps1 -Provider ollama -Model llama3.2:3b`
- [ ] Backend `.env` switched to `ollama`
- [ ] Backend restarted
- [ ] Confirm `/llm/health` changes provider correctly after restart
- [ ] `/llm/health` shows provider `ollama`
- [ ] `/llm/health` available `true`
- [ ] `/generate-cues` returns provider `ollama` or fallback provider if unavailable
- [ ] Frontend LLM status displays provider/model
- [ ] Frontend cue generation displays provider/risk flags/follow-up questions
- [ ] Mock provider still works after switching back
- [ ] Backend compile passes
- [ ] Frontend build passes
- [ ] Frontend lint passes
