from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MvpOrchestrationResult:
    run_id: str = ""
    goal_id: str = ""
    verdict: str = "UNKNOWN"
    action_status: str = ""
    artifacts: list[dict] = field(default_factory=list)
    events: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    evidence_refs: list[dict] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "goal_id": self.goal_id,
            "verdict": self.verdict,
            "action_status": self.action_status,
            "artifacts": list(self.artifacts),
            "events": list(self.events),
            "errors": list(self.errors),
            "evidence_refs": list(self.evidence_refs),
        }


class MvpFunctionalOrchestrator:
    def __init__(self) -> None:
        self._context: Any = None
        self._workspace: Any = None
        self._artifact_store: Any = None
        self._state_store: Any = None
        self._event_bus: Any = None
        self._action: Any = None
        self._contract_registry: Any = None
        self._capability_graph: Any = None
        self._policy_engine: Any = None
        self._decision_gate: Any = None
        self._invariant_engine: Any = None
        self._simulation_engine: Any = None
        self._executor: Any = None
        self._observer: Any = None
        self._review_interface: Any = None
        self._promotion_gate: Any = None
        self._circuit_breaker: Any = None
        self._rollback_controller: Any = None
        self._security_envelope: Any = None
        self._transaction_manager: Any = None
        self._runtime_profile: Any = None
        self._acceptance: Any = None

    def bind(self, component: str, instance: Any) -> None:
        setattr(self, f"_{component}", instance)

    def set_forbidden_actions(self, agent_id: str, actions: list[str]) -> None:
        if not hasattr(self, "_forbidden_actions_map"):
            self._forbidden_actions_map: dict[str, list[str]] = {}
        self._forbidden_actions_map[agent_id] = list(actions)

    def set_validator_files(self, files: list[str]) -> None:
        self._validator_files = list(files)

    def _validate_action(self, ctx: dict, run_id: str, goal_id: str,
                         errors: list[str]) -> bool:
        agent_id = ctx.get("agent_id", "default_agent")
        action_type = ctx.get("action_type", "")

        if self._contract_registry:
            contract = self._contract_registry.resolve(action_type)
            if contract is None:
                errors.append(f"No contract for action_type: {action_type}")
                return False

        if self._capability_graph:
            target = ctx.get("target", "report")
            allowed, reason = self._capability_graph.can(
                agent_id=agent_id, capability="execute", target=target,
            )
            if not allowed:
                errors.append(f"Capability denied: {reason}")
                return False

        forbidden_map = getattr(self, "_forbidden_actions_map", {})
        forbidden = forbidden_map.get(agent_id, [])
        if action_type in forbidden:
            errors.append(f"Forbidden action: {action_type} is not allowed for agent {agent_id}")
            return False

        if self._policy_engine:
            policy_ctx = {
                "agent_id": agent_id,
                "action_type": action_type,
                "target": ctx.get("target", "report"),
            }
            decision, reason = self._policy_engine.evaluate("action", policy_ctx, run_id=run_id)
            if decision != "ALLOW":
                errors.append(f"Policy denied: {reason}")
                return False

        if hasattr(self, "_validator_files"):
            target = ctx.get("target", "")
            if target in self._validator_files:
                errors.append(f"Validator alteration blocked: cannot modify {target}")
                return False

        return True

    def _write_evidence(self, run_id: str, action_id: str,
                        result: MvpOrchestrationResult,
                        clock: Any) -> None:
        if not self._artifact_store:
            return
        evidence = result.to_dict()
        self._artifact_store.write(
            run_id=run_id, action_id=action_id,
            name="evidence.json", data=evidence,
            artifact_type="evidence",
        )

    def _write_acceptance_output(self, result: MvpOrchestrationResult) -> None:
        if not self._acceptance:
            return
        self._acceptance.add_row(
            component=f"scenario:{result.goal_id}",
            status=result.verdict,
            details="; ".join(result.errors) if result.errors else "Accepted",
        )

    def run_goal(self, goal_text: str, profile_id: str = "STRICT",
                 context_overrides: dict | None = None) -> MvpOrchestrationResult:
        errors: list[str] = []
        ctx = context_overrides or {}

        if self._circuit_breaker and self._circuit_breaker.is_tripped:
            return MvpOrchestrationResult(errors=["Circuit breaker is tripped"])

        if self._context:
            self._context.initialize(goal_text=goal_text, profile_id=profile_id)
            run_id = self._context.run_id
            goal_id = self._context.goal_id
            clock = self._context.clock
            randomness = self._context.randomness
        else:
            run_id = ctx.get("run_id", "manual_run")
            goal_id = ctx.get("goal_id", "manual_goal")
            clock = None

        if self._workspace:
            self._workspace.create_run_workspace(run_id)
            self._workspace.create_temp_workspace(run_id)

        if self._state_store and run_id:
            self._state_store.create_record("goal", goal_id, run_id,
                                            {"text": goal_text, "profile_id": profile_id})

        if self._event_bus and run_id:
            from agentx_evolve.bus.event_bus import MvpEvent
            self._event_bus.publish(MvpEvent(
                message_id=randomness.next_id("evt_") if randomness else "evt_manual",
                event_type="goal_received", run_id=run_id,
                sender_id="orchestrator",
                payload={"goal_text": goal_text, "profile_id": profile_id},
                created_at=clock.now_iso() if clock else "",
            ))

        if self._action:
            self._action.propose()
            self._action.validate()

        valid = self._validate_action(ctx, run_id, goal_id, errors)
        if not valid:
            return MvpOrchestrationResult(
                run_id=run_id, goal_id=goal_id,
                verdict="VALIDATION_FAILED", errors=errors,
            )

        cap_ctx = {
            "agent_id": ctx.get("agent_id", "default_agent"),
            "capability": "execute",
            "target": ctx.get("target", "report"),
        }
        sim_ctx = {
            "action_type": ctx.get("action_type", "report_generation"),
            "target_path": ctx.get("target_path", "/dev/null"),
            "requires_rollback": ctx.get("requires_rollback", False),
        }

        if self._simulation_engine:
            sim_result = self._simulation_engine.simulate(self._action, sim_ctx)
            if not sim_result.safe_to_execute:
                return MvpOrchestrationResult(
                    run_id=run_id, goal_id=goal_id,
                    verdict="SIMULATION_FAILED", errors=[sim_result.reason],
                )

        gate_ctx = dict(cap_ctx)
        gate_ctx["scope"] = "action"
        gate_ctx["risk_level"] = ctx.get("risk_level", "low")
        gate_ctx["requires_rollback_plan"] = ctx.get("requires_rollback", False)
        gate_ctx["has_rollback_plan"] = ctx.get("has_rollback_plan", False)

        gate_out = None
        if self._decision_gate:
            gate_out = self._decision_gate.evaluate(self._action, gate_ctx)
            if gate_out.decision != "ALLOW":
                return MvpOrchestrationResult(
                    run_id=run_id, goal_id=goal_id,
                    verdict=f"GATE_DENIED_{gate_out.decision}",
                    errors=[gate_out.reason],
                )

        if self._action:
            self._action.simulate()
            self._action.approve()

        if self._security_envelope and self._context:
            from agentx_evolve.security.security_envelope import MvpEnvelopeBuilder
            envelope = (
                MvpEnvelopeBuilder()
                .with_run(run_id)
                .with_action(self._action.action_id)
                .with_agent(ctx.get("agent_id", "default_agent"))
                .with_workspace(str(self._workspace.root) if self._workspace else "")
                .with_profile(profile_id)
                .with_evidence_target(ctx.get("evidence_target", "default"))
                .build()
            )
            envelope.seal()

        txn = None
        if self._transaction_manager:
            txn = self._transaction_manager.begin(
                txn_id=randomness.next_id("txn_") if randomness else "txn_manual",
                run_id=run_id,
                action_id=self._action.action_id if self._action else "",
                created_at=clock.now_iso() if clock else "",
            )

        exec_result = None
        if self._executor:
            exec_ctx = {
                "run_id": run_id,
                "action_id": self._action.action_id if self._action else "",
                "report_content": ctx.get("report_content", {}),
                "report_name": ctx.get("report_name", "report.json"),
                "suppress_failure": ctx.get("suppress_failure", False),
            }
            exec_result = self._executor.execute(self._action, envelope if self._security_envelope else None, exec_ctx)

        if self._action:
            self._action.execute()

        if txn:
            txn_evidence = {"execution": exec_result} if exec_result else {}
            self._transaction_manager.stage(txn_evidence)
            self._transaction_manager.commit(
                committed_at=clock.now_iso() if clock else ""
            )

        obs_result = None
        if self._observer:
            obs_ctx = {
                "run_id": run_id,
                "expected_artifacts": [
                    {"path": a.get("path", "")}
                    for a in (exec_result or {}).get("artifacts", [])
                ],
            }
            obs_result = self._observer.observe(self._action, obs_ctx)

        if self._action:
            self._action.observe()
            self._action.test()

        packet_review_id = ""
        if self._review_interface:
            from agentx_evolve.review.review_interface import MvpReviewPacket
            packet = MvpReviewPacket(
                review_id=randomness.next_id("rev_") if randomness else "rev_manual",
                action_id=self._action.action_id if self._action else "",
                run_id=run_id,
                created_at=clock.now_iso() if clock else "",
            )
            self._review_interface.create_packet(packet)
            packet_review_id = packet.review_id

            review_decision = ctx.get("review_decision", "APPROVED")
            review_reason = ctx.get("review_reason", "Auto-approved")
            self._review_interface.record_decision(
                review_id=packet.review_id,
                decision=review_decision,
                reason=review_reason,
                reviewer=ctx.get("reviewer", "orchestrator"),
                decided_at=clock.now_iso() if clock else "",
            )

        if self._action:
            self._action.review()

        promote_ctx = {
            "run_id": run_id,
            "agent_id": ctx.get("agent_id", "default_agent"),
            "action_type": "promote",
            "review_ref": packet_review_id,
            "evidence_refs": (exec_result or {}).get("evidence_refs", []),
            "observation_ref": str(obs_result.action_id) if obs_result else "",
            "gate_result": gate_out.decision if gate_out else "",
            "invariant_pass": True,
        }
        if "target_agent" in ctx and ctx["target_agent"]:
            promote_ctx["target_agent"] = ctx["target_agent"]

        if self._invariant_engine:
            inv_results = self._invariant_engine.check_all(self._action, promote_ctx)
            promote_ctx["invariant_pass"] = all(
                r.get("passed", True) for r in inv_results
            )

        promotion_allowed = False
        if self._promotion_gate:
            prom_dec = self._promotion_gate.evaluate(self._action, promote_ctx)
            if prom_dec.promoted:
                if self._action:
                    self._action.promote()
                promotion_allowed = True
            else:
                if self._action:
                    self._action.reject()
                errors.extend(prom_dec.errors)

        err_text = str(errors).lower()
        if self._circuit_breaker and not promotion_allowed:
            self._circuit_breaker.trip(
                trigger="unsafe_self_promotion_attempt"
                if "self_promotion" in err_text or "self-promotion" in err_text else "invariant_violation",
                reason="; ".join(errors) if errors else "Promotion denied",
                action_id=self._action.action_id if self._action else "",
                run_id=run_id,
                timestamp=clock.now_iso() if clock else "",
            )

        if self._action:
            self._action.archive()

        verdict = "PASS" if promotion_allowed else "DENIED_AND_RECORDED"
        if errors and not promotion_allowed and "self_promotion" not in err_text and "self-promotion" not in err_text:
            verdict = "FAILED"

        result = MvpOrchestrationResult(
            run_id=run_id,
            goal_id=goal_id,
            verdict=verdict,
            action_status=self._action.status if self._action else "UNKNOWN",
            artifacts=(exec_result or {}).get("artifacts", []),
            errors=errors,
            evidence_refs=[
                {"gate": gate_out.decision if gate_out else "N/A"},
                *((exec_result or {}).get("evidence_refs", [])),
            ],
        )

        self._write_evidence(run_id, self._action.action_id if self._action else "", result, clock)
        self._write_acceptance_output(result)

        return result

    def replay_run(self, run_id: str, context: Any,
                   context_overrides: dict | None = None) -> MvpOrchestrationResult:
        if context is None:
            return MvpOrchestrationResult(errors=["Replay requires non-None context"])
        self._context = context
        return self.run_goal(
            goal_text=context.metadata.get("goal_text", "replay"),
            profile_id=context.profile_id or "STRICT",
            context_overrides=context_overrides,
        )
