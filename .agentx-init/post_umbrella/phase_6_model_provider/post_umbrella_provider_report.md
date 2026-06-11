# Phase 6 — Model Provider Abstraction Hardening

## Status: PASS

### Provider modes
1. **Deterministic fixture provider** — built-in for all 3 agents (clothing_fixture_read, planning_fixture_read, weather_fixture_read)
2. **Local provider adapter** — LLMProvider (opencode at http://127.0.0.1:14096)
3. **External provider interface** — disabled by default; requires explicit policy approval

### Provider rules implemented
- Stable interface: LLMProvider.complete(system_prompt, user_text, temperature)
- Schema-valid outputs: all planners validate model output through JSON parsing
- Malformed response rejected: PlannerPort raises RuntimeError on unparseable LLM output
- Provider identity recorded: evidence manifest records provider name and model
- Deterministic tests without external calls: fixture tools work independently
- Policy-gated: profile-based tool authorization
- No secret storage: provider configuration logged without secrets
- No direct source write: all outputs go through seed.emit_answer tool

### Provider tests
- All 65 fixture-based tests pass without LLM calls
- Integration tests verify LLM connectivity and response handling
