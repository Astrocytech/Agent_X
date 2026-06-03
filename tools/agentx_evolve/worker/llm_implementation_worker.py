from __future__ import annotations
from typing import Any
from agentx_evolve.worker.worker_models import (
    WorkerOutput, Change, ReplacementBlock,
    WO_PROPOSED, WO_NEEDS_MORE_CONTEXT, WO_FAILED,
    CT_UPDATE, CT_CREATE, CT_DELETE,
)
from agentx_evolve.context.context_models import (
    TaskPacket, TT_FIX_VALIDATION, TT_WRITE_TEST, TT_EXPLAIN_FAILURE,
)
from agentx_evolve.models.model_models import (
    ModelRequest, ModelResponse,
    MODEL_STATUS_SUCCESS, MODEL_STATUS_RETRYABLE,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST, TASK_EXPLAIN_FAILURE,
)
from agentx_evolve.models.prompt_runner import run_prompt
from agentx_evolve.models.model_models import ModelRegistry


class EditPlanGenerator:
    def generate(self, packet: TaskPacket) -> str:
        lines = [f"# Edit Plan for {packet.task_type}: {packet.objective}"]
        if packet.allowed_files:
            lines.append(f"## Allowed Files: {', '.join(packet.allowed_files)}")
        if packet.forbidden_files:
            lines.append(f"## Forbidden Files: {', '.join(packet.forbidden_files)}")
        if packet.allowed_files:
            for f in packet.allowed_files:
                lines.append(f"### {f}")
                lines.append(f"- Change type: UPDATE")
                lines.append(f"- Objective: {packet.objective}")
        return "\n".join(lines)


class PatchCandidateGenerator:
    def generate(self, packet: TaskPacket, plan: str,
                 model_response: ModelResponse | None = None) -> WorkerOutput:
        output = WorkerOutput(
            worker_output_id=f"wo-{__import__('uuid').uuid4().hex[:16]}",
            task_packet_id=packet.task_packet_id,
            status=WO_PROPOSED,
            edit_plan=plan,
        )
        if model_response and model_response.status == MODEL_STATUS_RETRYABLE:
            output.status = WO_NEEDS_MORE_CONTEXT
            output.warnings.append("Model reported insufficient context")
            return output
        for f in packet.allowed_files:
            output.changes.append(Change(
                target_file=f,
                change_type=CT_UPDATE,
                instructions=f"Implement: {packet.objective}",
            ))
        return output


class TestCandidateGenerator:
    def generate(self, packet: TaskPacket, plan: str) -> WorkerOutput:
        output = WorkerOutput(
            worker_output_id=f"wo-{__import__('uuid').uuid4().hex[:16]}",
            task_packet_id=packet.task_packet_id,
            status=WO_PROPOSED,
            edit_plan=plan,
        )
        if packet.allowed_files:
            for f in packet.allowed_files:
                test_file = f.replace(".py", "_test.py").replace("/", "/test_")
                output.changes.append(Change(
                    target_file=test_file,
                    change_type=CT_CREATE,
                    instructions=f"Write tests for {f}",
                ))
                output.tests_to_run.append(test_file)
        return output


class ValidationFixGenerator:
    def generate(self, packet: TaskPacket, plan: str,
                 test_output: str = "") -> WorkerOutput:
        output = WorkerOutput(
            worker_output_id=f"wo-{__import__('uuid').uuid4().hex[:16]}",
            task_packet_id=packet.task_packet_id,
            status=WO_PROPOSED,
            edit_plan=plan,
        )
        if test_output and any(kw in test_output.upper() for kw in ("FAILED", "ERROR")):
            output.status = WO_PROPOSED
            output.warnings.append(f"Validation output indicates failures")
        if packet.allowed_files:
            for f in packet.allowed_files:
                output.changes.append(Change(
                    target_file=f,
                    change_type=CT_UPDATE,
                    instructions=f"Fix validation: {packet.objective}",
                ))
        return output


class LLMImplementationWorker:
    def __init__(self, registry: ModelRegistry | None = None):
        self._registry = registry or ModelRegistry()
        self._plan_generator = EditPlanGenerator()
        self._patch_generator = PatchCandidateGenerator()
        self._test_generator = TestCandidateGenerator()
        self._fix_generator = ValidationFixGenerator()

    def process(self, packet: TaskPacket, test_output: str = "") -> WorkerOutput:
        plan = self._plan_generator.generate(packet)

        task_map = {
            TT_FIX_VALIDATION: self._fix_generator.generate,
            TT_WRITE_TEST: self._test_generator.generate,
        }

        if packet.task_type in task_map:
            kwargs = {}
            if packet.task_type == TT_FIX_VALIDATION:
                kwargs["test_output"] = test_output
            output = task_map[packet.task_type](packet, plan, **kwargs)
        else:
            model_request = ModelRequest(
                task_type=TASK_IMPLEMENT_PATCH,
                system_prompt=f"You are implementing: {packet.objective}",
                prompt=plan,
                json_only=True,
            )
            model_response = run_prompt(model_request, self._registry)
            output = self._patch_generator.generate(packet, plan, model_response)

            if model_response.raw_output:
                output.explanation = model_response.raw_output

        if packet.errors:
            for err in packet.errors:
                output.errors.append(err)
        if packet.forbidden_files:
            for change in output.changes:
                if change.target_file in packet.forbidden_files:
                    output.errors.append(
                        f"Cannot edit forbidden file: {change.target_file}"
                    )
                    output.status = WO_FAILED

        return output
