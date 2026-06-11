# Model Provider Configuration

## Supported Providers

| Provider | Mode | Status | Notes |
|----------|------|--------|-------|
| OpenCode (LLM) | Fixture | Active | Default provider for example agents. Uses `opencode` at localhost:14096. |
| Mock | Fixture | Active | Used in unit tests for deterministic LLM simulation. |
| Deterministic | Fixture | Active | Returns predefined outputs for testing. |

## Provider Interface

All providers implement `LLMProvider` with a single method:
```python
def complete(system_prompt: str, user_text: str, temperature: float = 0.0) -> str:
```

## Configuration
- Temperature is set to 0.0 for deterministic acceptance tests.
- Live provider mode is disabled by default.
- Network access requires explicit policy approval.
- Provider identity is recorded in evidence artifacts.

## Security
- Provider output cannot directly write source files.
- Provider output cannot self-promote.
- Provider output is validated against schema before acceptance.
