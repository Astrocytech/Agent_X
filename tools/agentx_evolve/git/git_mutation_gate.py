from agentx_evolve.git.git_models import (
    GitMutationRequest, GitOperationResult, GS_BLOCKED, GS_SUCCESS,
    GIT_EFFECT_STAGE, GIT_EFFECT_COMMIT, GIT_EFFECT_BRANCH,
    GIT_EFFECT_REVERT, GIT_EFFECT_PUSH,
    new_id, utc_now_iso,
)


class MutationGate:
    def check(self, req: GitMutationRequest) -> GitOperationResult:
        missing: list[str] = []
        if not req.policy_decision_id:
            missing.append("policy_decision_id")
        if not req.sandbox_decision_id:
            missing.append("sandbox_decision_id")
        if not req.promotion_gate_id:
            missing.append("promotion_gate_id")
        if missing:
            return GitOperationResult(
                result_id=new_id("gor"),
                operation_id=req.request_id,
                timestamp=utc_now_iso(),
                status=GS_BLOCKED,
                message=f"Missing required authorities: {', '.join(missing)}",
                errors=[f"Missing required authorities: {', '.join(missing)}"],
            )
        return GitOperationResult(
            result_id=new_id("gor"),
            operation_id=req.request_id,
            timestamp=utc_now_iso(),
            status=GS_SUCCESS,
            message="All gates passed",
            authority_refs={
                "policy_decision_id": req.policy_decision_id,
                "sandbox_decision_id": req.sandbox_decision_id,
                "promotion_gate_id": req.promotion_gate_id,
            },
        )
