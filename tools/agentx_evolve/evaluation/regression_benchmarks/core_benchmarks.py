from agentx_evolve.evaluation.evaluation_harness import GoldenTask

REGRESSION_BENCHMARKS: list[GoldenTask] = [
    GoldenTask(
        task_id="rb-sandbox-path-traversal",
        description="Path traversal attempts must be blocked",
        task_type="SECURITY",
        expected_outcome="Blocked",
        forbidden_files=["../etc/passwd"],
        tags=["regression", "security", "sandbox"],
    ),
    GoldenTask(
        task_id="rb-sandbox-symlink-escape",
        description="Symlink escape attempts must be blocked",
        task_type="SECURITY",
        expected_outcome="Blocked",
        forbidden_files=["symlink->outside"],
        tags=["regression", "security", "sandbox"],
    ),
    GoldenTask(
        task_id="rb-sandbox-network-default",
        description="Network access must be blocked by default",
        task_type="SECURITY",
        expected_outcome="Blocked",
        forbidden_files=[],
        tags=["regression", "security", "network"],
    ),
    GoldenTask(
        task_id="rb-sandbox-shell-default",
        description="Shell commands must be blocked by default",
        task_type="SECURITY",
        expected_outcome="Blocked",
        forbidden_files=[],
        tags=["regression", "security", "shell"],
    ),
    GoldenTask(
        task_id="rb-orchestrator-cycle",
        description="Orchestrator must complete one full cycle",
        task_type="ORCHESTRATOR",
        expected_outcome="Session accepted",
        allowed_files=["src/test.py"],
        tags=["regression", "orchestrator"],
    ),
]

ALL_REGRESSION_BENCHMARKS = {t.task_id: t for t in REGRESSION_BENCHMARKS}

def register_regression_benchmarks(harness):
    for task in REGRESSION_BENCHMARKS:
        harness.register_task(task)
