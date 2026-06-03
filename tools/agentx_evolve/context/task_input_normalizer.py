from __future__ import annotations

from agentx_evolve.context.context_models import TaskInput, new_id, utc_now_iso


SUSPICIOUS_PATTERNS = [
    "ignore previous instructions",
    "override system",
    "disable safety",
    "bypass policy",
    "execute this command",
    "skip validation",
    "mark done without tests",
    "hide from audit",
    "exfiltrate",
    "reveal secrets",
]


def normalize_task_input(raw_task: dict) -> TaskInput:
    task_title = raw_task.get("task_title", "") or ""
    task_description = raw_task.get("task_description", "") or ""

    if not task_title and not task_description:
        return TaskInput(
            task_input_id=new_id("ti"),
            created_at=utc_now_iso(),
            errors=["task_title or task_description is required"],
        )

    warnings: list[str] = []
    errors: list[str] = []

    embedded_warnings = _detect_suspicious_instructions(task_title, task_description)
    warnings.extend(embedded_warnings)

    for constraint in raw_task.get("user_constraints", []):
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern.lower() in constraint.lower():
                warnings.append(f"suspicious embedded instruction in constraint: {constraint[:80]}")
                break

    tools = sorted(raw_task.get("requested_tools", []))
    target_files = sorted(raw_task.get("target_files", []))
    forbidden = sorted(raw_task.get("forbidden_actions", []))
    required_outputs = sorted(raw_task.get("required_outputs", []))

    return TaskInput(
        task_input_id=raw_task.get("task_input_id", new_id("ti")),
        created_at=utc_now_iso(),
        source_component="ContextBuilderTaskPacker",
        task_title=task_title,
        task_description=task_description,
        task_type=raw_task.get("task_type", ""),
        user_constraints=raw_task.get("user_constraints", []),
        system_constraints=raw_task.get("system_constraints", []),
        required_outputs=required_outputs,
        forbidden_actions=forbidden,
        target_component_id=raw_task.get("target_component_id"),
        target_files=target_files,
        requested_tools=tools,
        requested_model_profile_id=raw_task.get("requested_model_profile_id"),
        requested_runtime_profile_id=raw_task.get("requested_runtime_profile_id"),
        warnings=warnings,
        errors=errors,
    )


def _detect_suspicious_instructions(title: str, description: str) -> list[str]:
    warnings: list[str] = []
    combined = f"{title} {description}"
    for pattern in SUSPICIOUS_PATTERNS:
        if pattern.lower() in combined.lower():
            warnings.append(f"suspicious instruction detected: '{pattern}'")
    return warnings
