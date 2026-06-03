from __future__ import annotations
import json
from pathlib import Path
from agentx_evolve.patch.patch_models import (
    PatchSession, PatchAction, ImplementationEvidence,
    MutationAllowlist, ApprovedMutation,
    SESSION_CREATED, SESSION_LOADED, SESSION_ACCEPTED, SESSION_ROLLED_BACK,
    SESSION_FAILED, SESSION_BLOCKED,
    new_id, utc_now_iso, to_dict,
)
from agentx_evolve.patch.file_change_guard import FileChangeGuard
from agentx_evolve.patch.patch_applier import PatchApplier
from agentx_evolve.patch.rollback_manager import RollbackManager
from agentx_evolve.patch.implementation_validation_gate import ImplementationValidationGate
from agentx_evolve.patch.implementation_evidence import ImplementationEvidenceWriter
from agentx_evolve.security.initiator_compat import InitiatorCompat
from agentx_evolve.security.sandbox_policy import SandboxPolicy
from agentx_evolve.security.security_models import (
    SandboxDecision, DECISION_ALLOW, DECISION_BLOCK,
)


class ImplementationSession:
    def __init__(
        self,
        repo_root: Path,
        policy: SandboxPolicy,
        session_id: str | None = None,
        proposal_id: str = "",
        governance_decision_id: str = "",
        risk_assessment_id: str = "",
        compat: InitiatorCompat | None = None,
        mutation_allowlist: MutationAllowlist | None = None,
    ):
        self._repo_root = repo_root.resolve()
        self._policy = policy
        self._session = PatchSession(
            session_id=session_id or new_id("sess"),
            timestamp=utc_now_iso(),
            proposal_id=proposal_id,
            governance_decision_id=governance_decision_id,
            risk_assessment_id=risk_assessment_id,
        )
        self._file_guard = FileChangeGuard(repo_root, policy)
        self._rollback = RollbackManager(repo_root)
        self._applier = PatchApplier(
            repo_root, policy,
            self._session.session_id,
            governance_decision_id,
            compat=compat,
            mutation_allowlist=mutation_allowlist,
        )
        self._validation_gate = ImplementationValidationGate(repo_root, policy)
        self._evidence = ImplementationEvidenceWriter(repo_root)
        self._snapshots: list = []
        self._mutation_allowlist = mutation_allowlist or self._resolve_allowlist_from_governance()

    @property
    def session_id(self) -> str:
        return self._session.session_id

    @property
    def session(self) -> PatchSession:
        return self._session

    def load_proposal(self, proposal: dict) -> PatchSession:
        self._session.status.transition_to(SESSION_LOADED)
        self._session.status.transition_to("PROPOSAL_LOADED")
        target_files = []
        actions = proposal.get("actions", proposal.get("proposed_changes", []))
        for act in actions:
            target_file = act.get("target_file", act.get("file", ""))
            if target_file:
                target_files.append(target_file)
            action = PatchAction(
                action_id=new_id("act"),
                timestamp=utc_now_iso(),
                target_file=target_file,
                change_type=act.get("change_type", act.get("type", "UPDATE")),
                old_text=act.get("old_text", ""),
                new_text=act.get("new_text", ""),
            )
            self._session.actions.append(action)

        self._session.target_paths = list(set(target_files))
        return self._session

    def _resolve_allowlist_from_governance(self) -> MutationAllowlist:
        gid = self._session.governance_decision_id
        if not gid:
            return MutationAllowlist()
        gov_path = self._repo_root / ".agentx-init" / "governance" / "decisions" / f"{gid}.json"
        if not gov_path.exists():
            return MutationAllowlist(warnings=[f"Governance decision not found: {gov_path}"])
        try:
            data = json.loads(gov_path.read_text())
        except (json.JSONDecodeError, OSError):
            return MutationAllowlist(errors=[f"Cannot read governance decision: {gov_path}"])
        mutations_data = data.get("mutation_allowlist", data.get("approved_mutations", []))
        mutations = []
        for m in mutations_data:
            mutations.append(ApprovedMutation(
                mutation_id=m.get("mutation_id", new_id("mut")),
                target_path=m.get("target_path", ""),
                allowed_change_types=m.get("allowed_change_types", ["UPDATE", "CREATE"]),
                governance_decision_id=gid,
                reason=m.get("reason", ""),
            ))
        return MutationAllowlist(
            allowlist_id=new_id("mal"),
            timestamp=utc_now_iso(),
            governance_decision_id=gid,
            mutations=mutations,
        )

    def check_governance(self) -> SandboxDecision:
        self._session.status.transition_to("GOVERNANCE_CHECKED")
        if not self._session.governance_decision_id:
            return SandboxDecision(
                decision_id=new_id("decision"),
                timestamp=utc_now_iso(),
                operation="EDIT",
                target=",".join(self._session.target_paths),
                decision=DECISION_BLOCK,
                reason="Governance decision ID is required",
            )
        if self._mutation_allowlist is None or self._mutation_allowlist.is_empty():
            self._mutation_allowlist = self._resolve_allowlist_from_governance()
        return SandboxDecision(
            decision_id=new_id("decision"),
            timestamp=utc_now_iso(),
            operation="EDIT",
            target=",".join(self._session.target_paths),
            decision=DECISION_ALLOW,
            reason="Governance check passed",
        )

    def apply_patch(self) -> PatchSession:
        for action in self._session.actions:
            guard_result = self._file_guard.check_change_allowed(
                action.target_file,
                implementation_session_id=self._session.session_id,
                governance_decision_id=self._session.governance_decision_id,
            )
            if guard_result.decision != DECISION_ALLOW:
                action.status = "BLOCKED"
                action.errors.append(guard_result.reason)
                self._session.errors.append(
                    f"Blocked: {action.target_file}: {guard_result.reason}"
                )
                continue

            action = self._applier.apply_action(action)

        self._session.status.transition_to("PATCH_APPLIED")
        return self._session

    def snapshot_before_apply(self) -> PatchSession:
        self._snapshots = self._rollback.snapshot_files(
            self._session.target_paths, self._session.session_id,
        )
        self._session.rollback_snapshot_paths = [
            s.snapshot_path for s in self._snapshots
        ]
        self._applier._rollback_id = self._session.session_id
        return self._session

    def validate(self, validation_commands: list[list[str]] | None = None) -> PatchSession:
        results = self._validation_gate.run_validation_commands(
            validation_commands or [],
        )
        self._session.validation_result = {
            "results": results,
            "all_passed": self._validation_gate.all_passed(results),
        }

        if self._validation_gate.all_passed(results):
            self._session.status.transition_to("VALIDATED")
        else:
            self._session.status.transition_to(SESSION_FAILED)
            for r in results:
                if r.get("status") != "PASS":
                    self._session.errors.append(
                        f"Validation failed: {' '.join(r.get('command', ['?']))}: "
                        f"{r.get('status')}: {r.get('stderr', '')[:200]}"
                    )

        return self._session

    def accept(self) -> PatchSession:
        self._session.status.transition_to(SESSION_ACCEPTED)
        self._evidence.write_evidence(ImplementationEvidence(
            evidence_id=new_id("ev"),
            timestamp=utc_now_iso(),
            session_id=self._session.session_id,
            event_type="SESSION_ACCEPTED",
            summary=f"Session {self._session.session_id} accepted",
            details={"target_paths": self._session.target_paths},
            artifact_refs=[f".agentx-init/implementation/sessions/{self._session.session_id}.json"],
        ))
        self._write_session()
        return self._session

    def rollback(self) -> PatchSession:
        results = self._rollback.restore_all(self._snapshots)
        self._session.status.transition_to(SESSION_ROLLED_BACK)
        self._evidence.write_evidence(ImplementationEvidence(
            evidence_id=new_id("ev"),
            timestamp=utc_now_iso(),
            session_id=self._session.session_id,
            event_type="SESSION_ROLLED_BACK",
            summary=f"Session {self._session.session_id} rolled back",
            details={"restore_results": results},
        ))
        self._write_session()
        return self._session

    def fail(self, reason: str = "") -> PatchSession:
        try:
            self._session.status.transition_to(SESSION_FAILED)
        except ValueError:
            pass
        self._session.errors.append(reason or "Session failed")
        self._write_session()
        return self._session

    def _write_session(self) -> Path:
        path = (
            self._repo_root / ".agentx-init" / "implementation" / "sessions"
            / f"{self._session.session_id}.json"
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self._session.to_dict(), indent=2, default=str))
        self._session.evidence_refs.append(str(path))
        return path
