from __future__ import annotations

import json
from typing import Any

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerModelResponse,
    ParsedModelOutput,
    LLMWorkerResult,
    utc_now_iso,
    new_id,
    sha256_dict,
    redact_secret_like,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    WORKER_INVALID,
    WORKER_FAILED,
    MODEL_RESPONSE_STATUS_SUCCESS,
)
from agentx_evolve.workers.llm_implementation_worker.worker_errors import (
    WORKER_MODEL_RESPONSE_INVALID,
    WORKER_MODEL_OUTPUT_REJECTED,
)


REJECTION_PATTERNS = [
    "already changed",
    "already modified",
    "already updated",
    "tests passed",
    "tests already pass",
    "commands were executed",
    "shell execution completed",
    "patch has been applied",
    "git commit",
    "git push",
    "files were written",
    "source was modified",
]

DIRECT_EXECUTION_PATTERNS = [
    "subprocess.run",
    "subprocess.Popen",
    "os.system",
    "os.popen",
    "pathlib.Path.write_text",
    "open().write",
    "git add",
    "git commit",
    "git push",
    "patch.apply",
    "apply_patch",
]


def parse_model_output(
    model_response: LLMWorkerModelResponse,
) -> ParsedModelOutput:
    parsed = ParsedModelOutput(
        parsed_output_id=new_id("po"),
        created_at=utc_now_iso(),
        task_id=model_response.task_id,
        model_response_id=model_response.model_response_id,
    )

    if not model_response.is_success():
        parsed.errors.append(
            f"Cannot parse: model response status is {model_response.status}"
        )
        parsed.parsed_output_hash = sha256_dict(parsed.to_dict())
        return parsed

    raw = model_response.raw_response_ref
    if raw is None:
        safe = model_response.safe_summary
    else:
        safe = raw

    structured = _try_parse_json(safe)

    if structured is None:
        parsed.errors.append("Model output could not be parsed as JSON")
        parsed.parsed_output_hash = sha256_dict(parsed.to_dict())
        return parsed

    parsed.implementation_summary = structured.get("implementation_summary", "")
    parsed.implementation_plan = structured.get("implementation_plan", {})
    parsed.files_to_change = structured.get("files_to_change", [])
    parsed.schemas_to_change = structured.get("schemas_to_change", [])
    parsed.tests_to_change = structured.get("tests_to_change", [])
    parsed.patch_proposal = structured.get("patch_proposal")
    parsed.validation_handoff = structured.get("validation_handoff")
    parsed.risk_notes = structured.get("risk_notes", [])
    parsed.assumptions = structured.get("assumptions", [])

    rejected = _find_rejected_content(safe)
    parsed.rejected_content = rejected

    redacted_summary = _redact_output(parsed.implementation_summary)
    parsed.implementation_summary = redacted_summary

    parsed.parsed_output_hash = sha256_dict(parsed.to_dict())

    return parsed


def _try_parse_json(raw: str) -> dict | None:
    if not raw or not raw.strip():
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    import re
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None


def _find_rejected_content(raw: str) -> list[dict]:
    rejected = []
    raw_lower = raw.lower()
    for pattern in REJECTION_PATTERNS:
        if pattern in raw_lower:
            rejected.append({
                "pattern": pattern,
                "severity": "rejected",
                "reason": f"Model output contains prohibited claim: '{pattern}'",
            })
    for pattern in DIRECT_EXECUTION_PATTERNS:
        if pattern in raw_lower:
            rejected.append({
                "pattern": pattern,
                "severity": "blocked",
                "reason": f"Model output contains direct execution: '{pattern}'",
            })
    return rejected


def _redact_output(value: str) -> str:
    return redact_secret_like(value)


def validate_parsed_model_output(
    parsed_output: ParsedModelOutput,
    task: LLMWorkerTask,
) -> LLMWorkerResult | None:
    errors = []

    if not parsed_output.implementation_summary:
        errors.append("Missing required field: implementation_summary")

    if not parsed_output.implementation_plan:
        errors.append("Missing required field: implementation_plan")

    for rc in parsed_output.rejected_content:
        if rc.get("severity") in ("rejected", "blocked"):
            errors.append(rc.get("reason", "Output rejected"))

    if errors:
        return LLMWorkerResult(
            worker_result_id=new_id("wr"),
            created_at=utc_now_iso(),
            task_id=task.task_id,
            status=WORKER_INVALID,
            message="Parsed model output validation failed",
            worker_mode=task.worker_mode,
            failure_class=WORKER_MODEL_OUTPUT_REJECTED,
            errors=errors,
        )

    return None
