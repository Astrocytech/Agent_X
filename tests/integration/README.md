# Integration tests

Cross-component tests that verify interactions between layers and tools.

Rules:
- Tests may exercise real component boundaries.
- Must not require live network access unless marked `@pytest.mark.live`.
- Integration tests should be fast enough to run in CI.
