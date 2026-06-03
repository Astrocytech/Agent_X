from __future__ import annotations
from typing import Any, Callable
from agentx_evolve.orchestrator.session_models import (
    SessionRecord, SESSION_TRANSITIONS, MAX_REPAIR_LOOPS,
    SC_CREATED, SC_SCANNED, SC_PLANNED, SC_PROPOSED,
    SC_GOVERNANCE_CHECKED, SC_CONTEXT_BUILT, SC_MODEL_PROPOSED,
    SC_PATCH_APPLIED, SC_VALIDATED, SC_ROLLED_BACK,
    SC_ACCEPTED, SC_FAILED, SC_BLOCKED,
)
from agentx_evolve.context.context_builder import ContextBuilder
from agentx_evolve.context.task_packet import TaskPacket
from agentx_evolve.worker.llm_implementation_worker import LLMImplementationWorker
from agentx_evolve.worker.worker_models import WorkerOutput, WO_PROPOSED, WO_FAILED


class SelfEvolutionOrchestrator:
    def __init__(self, context_builder: ContextBuilder | None = None,
                 worker: LLMImplementationWorker | None = None):
        self._context_builder = context_builder or ContextBuilder()
        self._worker = worker or LLMImplementationWorker()
        self._hooks: dict[str, Callable] = {
            "plan": lambda: [{"id": "default-c1", "description": "system evolution"}],
            "propose": lambda: {"proposal_id": "default-prop-1"},
            "governance_check": lambda: {"decision": "ALLOW", "level": "L1"},
            "risk_assessment": lambda: {"level": "low"},
            "apply_patch": lambda: {"status": "applied", "session_id": "default-ps-1"},
            "validate": lambda: {"passed": True, "output": ""},
            "scan": lambda: {"status": "ok", "findings": []},
            "status": lambda: {"status": "ok"},
        }

    def register_hook(self, name: str, fn: Callable) -> None:
        self._hooks[name] = fn

    def _call_hook(self, name: str, *args, **kwargs) -> Any:
        fn = self._hooks.get(name)
        if fn:
            return fn(*args, **kwargs)
        return None

    def run_cycle(self, session: SessionRecord,
                  candidate_files: list[str] | None = None,
                  ) -> SessionRecord:
        if session.is_terminal():
            return session

        # 1. Scan
        if not self._step_scan(session):
            return session
        # 2. Status
        if not self._step_status(session):
            return session
        # 3. Plan
        if not self._step_plan(session):
            return session
        # 4. Select candidate
        if not self._step_select(session):
            return session
        # 5. Propose
        if not self._step_propose(session):
            return session
        # 6. Governance check
        if not self._step_governance(session):
            return session
        # 7. Build task packet
        packet = self._step_build_context(session, candidate_files)
        if packet is None:
            return session
        # 8. LLM worker
        if not self._step_worker(session, packet):
            return session
        # 9. Apply patch
        if not self._step_apply_patch(session):
            return session
        # 10. Validate
        if not self._step_validate(session):
            return session
        # 11. Accept or repair
        self._step_finalize(session, packet)

        # 14. Completion record
        self._step_complete(session)

        return session

    def _step_scan(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_SCANNED):
            return True
        result = self._call_hook("scan") or {"status": "ok", "findings": []}
        session.scan_result = result
        session.transition_to(SC_SCANNED)
        return True

    def _step_status(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_PLANNED):
            return True
        result = self._call_hook("status") or {"status": "ok"}
        session.status_result = result
        session.transition_to(SC_PLANNED)
        return True

    def _step_plan(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_PROPOSED):
            return True
        result = self._call_hook("plan") or []
        session.plan_result = result
        if not result:
            session.transition_to(SC_BLOCKED)
            session.errors.append("No plan candidates available")
            return False
        session.transition_to(SC_PROPOSED)
        return True

    def _step_select(self, session: SessionRecord) -> bool:
        if session.status != SC_PROPOSED:
            return True
        candidates = session.plan_result or []
        if not candidates:
            session.transition_to(SC_BLOCKED)
            session.errors.append("No candidates to select from")
            return False
        selected = self._call_hook("select_candidate") or candidates[0]
        session.selected_candidate = selected
        return True

    def _step_propose(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_GOVERNANCE_CHECKED):
            return True
        result = self._call_hook("propose") or {"proposal_id": "prop-1"}
        session.proposal_result = result
        session.transition_to(SC_GOVERNANCE_CHECKED)
        return True

    def _step_governance(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_CONTEXT_BUILT):
            return True
        gov = self._call_hook("governance_check") or {"decision": "ALLOW", "level": "L1"}
        risk = self._call_hook("risk_assessment") or {"level": "low"}
        session.governance_result = gov
        session.risk_assessment = risk
        if gov.get("decision") != "ALLOW":
            session.transition_to(SC_BLOCKED)
            session.errors.append(f"Governance denied: {gov.get('decision')}")
            return False
        session.transition_to(SC_CONTEXT_BUILT)
        return True

    def _step_build_context(self, session: SessionRecord,
                            candidate_files: list[str] | None) -> TaskPacket | None:
        if not session.can_transition_to(SC_MODEL_PROPOSED):
            return None
        objective = (session.selected_candidate or {}).get("description", "")
        packet = self._context_builder.build_packet(
            task_type="IMPLEMENT_PATCH",
            objective=objective or session.description or "evolve",
            candidate_files=candidate_files,
            governance_result=session.governance_result,
            risk_assessment=session.risk_assessment,
        )
        session.task_packet_id = packet.task_packet_id
        session.transition_to(SC_MODEL_PROPOSED)
        return packet

    def _step_worker(self, session: SessionRecord, packet: TaskPacket) -> bool:
        if not session.can_transition_to(SC_PATCH_APPLIED):
            return True
        output = self._worker.process(packet)
        session.worker_output_id = output.worker_output_id
        if output.status == WO_FAILED:
            session.transition_to(SC_FAILED)
            for e in output.errors:
                session.errors.append(e)
            return False
        session.transition_to(SC_PATCH_APPLIED)
        return True

    def _step_apply_patch(self, session: SessionRecord) -> bool:
        if not session.can_transition_to(SC_VALIDATED):
            return True
        result = self._call_hook("apply_patch") or {"status": "applied", "session_id": "ps-1"}
        if result.get("status") in ("applied", "ok"):
            session.patch_session_id = result.get("session_id", "")
            session.transition_to(SC_VALIDATED)
            return True
        session.transition_to(SC_ROLLED_BACK)
        session.errors.append(f"Patch apply failed: {result.get('status')}")
        self._call_hook("rollback")
        return False

    def _step_validate(self, session: SessionRecord) -> bool:
        if session.status != SC_VALIDATED:
            return True
        result = self._call_hook("validate") or {"passed": True, "output": ""}
        session.validation_result = result
        return True

    def _step_finalize(self, session: SessionRecord, packet: TaskPacket) -> None:
        if session.status != SC_VALIDATED:
            return
        validation = session.validation_result or {}
        if validation.get("passed", False):
            session.transition_to(SC_ACCEPTED)
            return
        if session.repair_count >= MAX_REPAIR_LOOPS:
            session.transition_to(SC_BLOCKED)
            session.errors.append(f"Exceeded {MAX_REPAIR_LOOPS} repair loops")
            return
        session.repair_count += 1
        session.warnings.append(
            f"Validation failed, repair attempt {session.repair_count}/{MAX_REPAIR_LOOPS}"
        )
        fix_packet = self._context_builder.build_packet(
            task_type="FIX_VALIDATION",
            objective=f"Fix validation: {validation.get('output', '')}",
            candidate_files=packet.allowed_files,
        )
        fix_output = self._worker.process(fix_packet,
                                          test_output=validation.get("output", ""))
        if fix_output.status == WO_FAILED:
            session.transition_to(SC_ROLLED_BACK)
            self._call_hook("rollback")
            return
        session.task_packet_id = fix_packet.task_packet_id
        session.worker_output_id = fix_output.worker_output_id
        session.transition_to(SC_MODEL_PROPOSED)

    def _step_complete(self, session: SessionRecord) -> None:
        session.completion_record = {
            "session_id": session.session_id,
            "final_status": session.status,
            "repair_count": session.repair_count,
        }
        self._call_hook("record_evidence", session.to_dict())
