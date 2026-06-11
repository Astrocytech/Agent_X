from agentx_evolve.security.security_envelope import (
    MvpSecurityEnvelope, MvpEnvelopeBuilder, MvpEnvelopeValidator,
)


class TestMvpSecurityEnvelope:
    def test_builder_creates_valid_envelope(self):
        env = (MvpEnvelopeBuilder()
               .with_run("run-1")
               .with_action("act-1")
               .with_agent("agent-1")
               .with_workspace("/ws")
               .with_profile("STRICT")
               .with_evidence_target("evidence")
               .build())
        assert env.is_valid()

    def test_missing_fields_fail_validation(self):
        env = MvpSecurityEnvelope()
        issues = env.validate()
        assert len(issues) > 0
        assert not env.is_valid()

    def test_sealed_cannot_be_changed(self):
        env = MvpSecurityEnvelope(run_id="r1", action_id="a1", agent_identity="ag1",
                                  workspace_id="w1", runtime_profile_id="p1",
                                  evidence_target="e1")
        env.seal()
        assert env.is_sealed()

    def test_validator_checks_envelope(self):
        env = (MvpEnvelopeBuilder()
               .with_run("r1").with_action("a1").with_agent("ag1")
               .with_workspace("w1").with_profile("p1").with_evidence_target("e1")
               .build())
        env.seal()
        issues = MvpEnvelopeValidator.validate_envelope(env, {"agent_id": "ag1"})
        assert len(issues) == 0

    def test_validator_detects_mismatch(self):
        env = (MvpEnvelopeBuilder()
               .with_run("r1").with_action("a1").with_agent("ag1")
               .with_workspace("w1").with_profile("p1").with_evidence_target("e1")
               .build())
        env.seal()
        issues = MvpEnvelopeValidator.validate_envelope(env, {"agent_id": "wrong"})
        assert len(issues) > 0
