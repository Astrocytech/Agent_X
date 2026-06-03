from __future__ import annotations

import json

from agentx_evolve.workers.llm_implementation_worker.worker_models import (
    LLMWorkerTask,
    LLMWorkerContextPackage,
    LLMWorkerPromptPackage,
    utc_now_iso,
    new_id,
    sha256_dict,
)
from agentx_evolve.workers.llm_implementation_worker.worker_config import (
    SOURCE_COMPONENT,
)


FORBIDDEN_ACTIONS = [
    "direct source write",
    "direct shell execution",
    "direct subprocess execution",
    "direct Git write",
    "direct patch application",
    "direct model provider call",
    "direct network call",
    "direct MCP server call",
    "policy bypass",
    "sandbox bypass",
    "tool adapter bypass",
    "model adapter bypass",
    "patch execution bypass",
    "governance bypass",
    "human approval bypass",
]

REQUIRED_OUTPUT_SECTIONS = [
    "implementation_summary",
    "implementation_plan",
    "files_to_change",
    "risk_notes",
    "assumptions",
]


def build_prompt_package(
    task: LLMWorkerTask,
    context_package: LLMWorkerContextPackage,
    output_schema_id: str,
) -> LLMWorkerPromptPackage:
    pkg = LLMWorkerPromptPackage(
        prompt_package_id=new_id("pp"),
        created_at=utc_now_iso(),
        task_id=task.task_id,
        context_package_id=context_package.context_package_id,
    )

    system_contract_lines = [
        f"You are an implementation worker for component: {task.target_component_id}.",
        "You produce structured implementation plans, patch proposals, and validation requests.",
        "You do not execute code, apply patches, run tests, or modify files.",
        "You must follow Agent_X governance rules at all times.",
    ]
    if task.constraints:
        system_contract_lines.append("")
        system_contract_lines.append("Constraints:")
        for c in task.constraints:
            system_contract_lines.append(f"- {c}")

    pkg.system_contract = "\n".join(system_contract_lines)

    developer_contract_lines = [
        "Implementation Goal:",
        task.implementation_goal,
        "",
        "Context Summary:",
        context_package.context_summary,
        "",
    ]
    if context_package.included_files:
        developer_contract_lines.append("Context Files Included:")
        for f in context_package.included_files:
            developer_contract_lines.append(f"  - {f}")
    pkg.developer_contract = "\n".join(developer_contract_lines)

    pkg.task_prompt = task.implementation_goal

    pkg.output_schema_instruction = build_output_schema_instruction(output_schema_id)

    pkg.forbidden_actions = list(FORBIDDEN_ACTIONS)

    pkg.required_output_sections = list(REQUIRED_OUTPUT_SECTIONS)

    pkg.prompt_hash = hash_prompt_package(pkg)

    return pkg


def build_output_schema_instruction(schema_id: str) -> str:
    instructions = {
        "llm_worker_model_output.schema.json": (
            "Produce structured JSON output with the following sections:\n"
            '  - "implementation_summary": string\n'
            '  - "implementation_plan": object with steps, files_expected_to_change, '
            "schemas_expected_to_change, tests_expected_to_change, risk_notes\n"
            '  - "files_to_change": list of file paths\n'
            '  - "schemas_to_change": list of schema file paths\n'
            '  - "tests_to_change": list of test file paths\n'
            '  - "patch_proposal": optional object with patch_format, target_files, '
            "proposed_changes, rationale\n"
            '  - "validation_handoff": optional object with validation_commands, '
            "expected_artifacts\n"
            '  - "risk_notes": list of strings\n'
            '  - "assumptions": list of strings\n'
            "Do not claim files were changed, tests passed, or commands were executed."
        ),
    }
    return instructions.get(
        schema_id,
        f"Produce structured output conforming to schema: {schema_id}",
    )


def hash_prompt_package(prompt_package: LLMWorkerPromptPackage) -> str:
    data = {
        "system_contract": prompt_package.system_contract,
        "developer_contract": prompt_package.developer_contract,
        "task_prompt": prompt_package.task_prompt,
        "output_schema_instruction": prompt_package.output_schema_instruction,
        "forbidden_actions": prompt_package.forbidden_actions,
        "required_output_sections": prompt_package.required_output_sections,
    }
    return sha256_dict(data)
