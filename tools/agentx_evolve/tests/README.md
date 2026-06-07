# agentx_evolve tests

This folder contains unit and component tests for `tools/agentx_evolve`.

Rules:
- No live network calls by default.
- Use mock providers unless a test is explicitly marked live.
- Runtime artifacts must be written only to temporary test directories.
- Tests must not mutate repository source files unless the test creates a disposable copy.
- Cross-package integration tests belong in root `tests/integration/`.
