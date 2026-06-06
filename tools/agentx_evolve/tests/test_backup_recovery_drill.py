import pytest
from agentx_evolve.backup.disaster_recovery_plan import RecoveryDrill, DrillResult, DD_PASS, DD_FAIL


class TestDrillConstants:
    def test_dd_pass_value(self):
        assert DD_PASS == "PASS"

    def test_dd_fail_value(self):
        assert DD_FAIL == "FAIL"


class TestDrillResult:
    def test_defaults(self):
        result = DrillResult()
        assert result.status == DD_PASS
        assert result.summary == ""

    def test_failure_result(self):
        result = DrillResult(status=DD_FAIL, summary="Backup verification failed")
        assert result.status == DD_FAIL
        assert result.summary == "Backup verification failed"


class TestRecoveryDrill:
    def test_defaults(self):
        drill = RecoveryDrill()
        assert drill.drill_id == ""
        assert drill.result is None

    def test_drill_records_success(self):
        result = DrillResult(status=DD_PASS)
        drill = RecoveryDrill(drill_id="drill_001", scope="full", result=result)
        assert drill.drill_id == "drill_001"
        assert drill.result.status == DD_PASS

    def test_drill_records_failure(self):
        result = DrillResult(status=DD_FAIL)
        drill = RecoveryDrill(drill_id="drill_002", scope="partial", result=result)
        assert drill.result.status == DD_FAIL

    def test_drill_tracks_timestamp_and_scope(self):
        ts = "2025-01-01T00:00:00"
        drill = RecoveryDrill(drill_id="drill_003", timestamp=ts, scope="incremental")
        assert drill.timestamp == ts
        assert drill.scope == "incremental"
