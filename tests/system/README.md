# System tests

End-to-end tests that exercise full commands and workflows.

Rules:
- Tests should run a complete command from start to finish.
- Must use temporary directories for any runtime artifacts.
- Use `@pytest.mark.live` for tests that require external providers.
