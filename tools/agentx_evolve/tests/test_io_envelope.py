from agentx_evolve.io.result_envelope import MvpResultEnvelope, validate_envelope, register_record_type


class TestMvpResultEnvelope:
    def test_valid_envelope_passes(self):
        register_record_type("test_result")
        env = MvpResultEnvelope(
            run_id="run-1", producer_id="producer-1",
            record_type="test_result", status="PASS",
            created_at="2026-06-10T12:00:00",
        )
        assert env.is_valid()

    def test_missing_run_id_fails(self):
        env = MvpResultEnvelope(producer_id="p1", record_type="r", status="PASS")
        assert not env.is_valid()
        assert "run_id is required" in env.validate()

    def test_invalid_status_fails(self):
        env = MvpResultEnvelope(
            run_id="r1", producer_id="p1", record_type="r", status="INVALID",
        )
        assert not env.is_valid()

    def test_pass_with_errors_fails(self):
        env = MvpResultEnvelope(
            run_id="r1", producer_id="p1", record_type="r",
            status="PASS", errors=["error"],
        )
        assert not env.is_valid()

    def test_from_dict_roundtrip(self):
        register_record_type("test")
        data = {
            "schema_version": "1.0.0",
            "run_id": "r1", "producer_id": "p1",
            "record_type": "test", "status": "PASS",
            "payload": {"a": 1}, "errors": [], "warnings": [],
            "evidence_refs": [], "created_at": "2026-01-01",
        }
        env = MvpResultEnvelope.from_dict(data)
        assert env.run_id == "r1"
        assert env.is_valid()

    def test_validate_envelope_function(self):
        register_record_type("validate_test")
        ok, issues = validate_envelope({
            "run_id": "r1", "producer_id": "p1",
            "record_type": "validate_test", "status": "PASS",
        })
        assert ok
        assert len(issues) == 0
