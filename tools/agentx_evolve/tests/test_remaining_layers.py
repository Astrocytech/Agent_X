import pytest
from agentx_evolve.review.review_interface import (
    ApprovalRecord, ReviewReport, ApprovalHistory, HumanReviewInterface,
    AD_PENDING, AD_APPROVED, AD_REJECTED,
)
from agentx_evolve.promotion.promotion_models import (
    PromotionGateDecision,
    PC_APPROVED, PC_BLOCKED, PC_NEEDS_APPROVAL,
)
from agentx_evolve.learning.outcome_models import OutcomeEvent
from agentx_evolve.learning.outcome_review import LearningOutcomeRecord, LearningOutcomeReview, StrategyMemory
from agentx_evolve.queue.task_queue import TaskQueueItem, TaskQueue, QS_PENDING, QS_RUNNING
from agentx_evolve.evaluation.evaluation_harness import (
    GoldenTask, EvalResult, EvalSuiteResult, EvaluationHarness, QualityScorecard,
)
from agentx_evolve.docsync.doc_sync import DocDrift, DocSyncResult, DocSyncChecker, SchemaDocChecker
from agentx_evolve.runtime.runtime_profile import (
    RuntimeProfile, ModelResourceBudget, DEFAULT_PROFILES,
    RP_CPU_ONLY_SAFE, RP_SMALL_GPU_8GB, RP_BALANCED_LOCAL, RP_HOSTED_FALLBACK,
)
from agentx_evolve.monitoring.monitoring import AuditEvent, AuditLog, SessionInspector
from agentx_evolve.acceptance.acceptance import AcceptanceCheck, AC_CHECK_PASS
from agentx_evolve.orchestrator.orchestrator_models import (
    OrchestrationSession,
)


# ---------------------------------------------------------------------------
# Human Review / Approval Interface tests
# ---------------------------------------------------------------------------

def test_approval_record_defaults():
    r = ApprovalRecord()
    assert r.decision == AD_PENDING
    assert not r.is_decided()


def test_approval_record_decided():
    r = ApprovalRecord(decision=AD_APPROVED)
    assert r.is_decided()


def test_approval_record_to_dict():
    r = ApprovalRecord(approval_id="a1")
    d = r.to_dict()
    assert d["approval_id"] == "a1"


def test_review_report_defaults():
    r = ReviewReport()
    assert r.files_changed == []


def test_review_report_to_dict():
    r = ReviewReport(session_id="s1", files_changed=["a.py"])
    d = r.to_dict()
    assert d["session_id"] == "s1"


def test_approval_history():
    h = ApprovalHistory()
    r = ApprovalRecord(approval_id="a1", session_id="s1", decision=AD_APPROVED)
    h.add(r)
    assert h.get("a1") is r
    assert h.is_session_approved("s1")
    assert not h.is_session_approved("s2")


def test_approval_history_get_by_session():
    h = ApprovalHistory()
    h.add(ApprovalRecord(approval_id="a1", session_id="s1"))
    h.add(ApprovalRecord(approval_id="a2", session_id="s1"))
    assert len(h.get_by_session("s1")) == 2


def test_human_review_interface():
    hri = HumanReviewInterface()
    assert hri.history is not None


def test_human_review_approve():
    hri = HumanReviewInterface()
    r = hri.approve("s1", reviewer="alice", reason="looks good")
    assert r.decision == AD_APPROVED
    assert r.reviewer == "alice"
    assert hri.is_approved("s1")


def test_human_review_reject():
    hri = HumanReviewInterface()
    r = hri.reject("s1", reviewer="bob", reason="needs work")
    assert r.decision == AD_REJECTED
    assert not hri.is_approved("s1")


def test_human_review_report():
    hri = HumanReviewInterface()
    report = ReviewReport(session_id="s1", task="fix bug")
    result = hri.review("s1", report)
    assert result.task == "fix bug"


# ---------------------------------------------------------------------------
# Promotion / Release Gate tests
# ---------------------------------------------------------------------------

def test_promotion_gate_decision_defaults():
    d = PromotionGateDecision()
    assert d.status == PC_BLOCKED


def test_promotion_gate_decision_approved():
    d = PromotionGateDecision(status=PC_APPROVED)
    assert d.status == PC_APPROVED


def test_promotion_gate_decision_blocked():
    d = PromotionGateDecision(status=PC_BLOCKED)
    assert d.status == PC_BLOCKED


def test_promotion_gate_decision_needs_approval():
    d = PromotionGateDecision(status=PC_NEEDS_APPROVAL)
    assert d.status == PC_NEEDS_APPROVAL


# ---------------------------------------------------------------------------
# Learning / Outcome Review tests
# ---------------------------------------------------------------------------

def test_outcome_record_defaults():
    r = LearningOutcomeRecord()
    assert r.outcome_id == ""


def test_outcome_review_record():
    o = LearningOutcomeReview()
    r = LearningOutcomeRecord(session_id="s1", attempted_task="fix parser",
                              successful_strategy="replaced regex")
    o.record(r)
    assert len(o.list_all()) == 1
    assert r.outcome_id.startswith("or-")


def test_outcome_review_get_by_session():
    o = LearningOutcomeReview()
    o.record(LearningOutcomeRecord(session_id="s1"))
    o.record(LearningOutcomeRecord(session_id="s2"))
    assert len(o.get_by_session("s1")) == 1


def test_outcome_review_successful_strategies():
    o = LearningOutcomeReview()
    o.record(LearningOutcomeRecord(session_id="s1", successful_strategy="X"))
    o.record(LearningOutcomeRecord(session_id="s2", failure_reason="Y"))
    assert len(o.get_successful_strategies()) == 1


def test_outcome_review_failure_patterns():
    o = LearningOutcomeReview()
    o.record(LearningOutcomeRecord(failure_reason="timeout"))
    assert len(o.get_failure_patterns()) == 1


def test_outcome_review_recommendations():
    o = LearningOutcomeReview()
    o.record(LearningOutcomeRecord(future_recommendation="use smaller model"))
    o.record(LearningOutcomeRecord(future_recommendation=""))
    assert len(o.get_recommendations()) == 1


def test_strategy_memory():
    m = StrategyMemory()
    m.store("key1", "value1")
    assert m.retrieve("key1") == "value1"
    assert m.retrieve("nonexistent") is None


def test_strategy_memory_search():
    m = StrategyMemory()
    m.store("patch:parser", "use regex")
    m.store("patch:lexer", "use state machine")
    m.store("test:parser", "mock input")
    assert len(m.search("patch:")) == 2


def test_strategy_memory_clear():
    m = StrategyMemory()
    m.store("k1", "v1")
    m.clear()
    assert m.retrieve("k1") is None


# ---------------------------------------------------------------------------
# Task Queue tests
# ---------------------------------------------------------------------------

def test_task_queue_item_defaults():
    i = TaskQueueItem()
    assert i.status == QS_PENDING


def test_task_queue_enqueue():
    q = TaskQueue()
    item = q.enqueue("s1", "fix parser", priority=1)
    assert item.session_id == "s1"
    assert item.item_id.startswith("tq-")


def test_task_queue_get():
    q = TaskQueue()
    item = q.enqueue("s1", "fix")
    assert q.get(item.item_id) is item


def test_task_queue_list_all():
    q = TaskQueue()
    q.enqueue("s1", "fix parser", priority=2)
    q.enqueue("s2", "write test", priority=1)
    items = q.list_all()
    assert len(items) == 2


def test_task_queue_filter_by_status():
    q = TaskQueue()
    i1 = q.enqueue("s1", "fix")
    q.enqueue("s2", "done")
    q.update_status(i1.item_id, QS_RUNNING)
    pending = q.list_all(status=QS_RUNNING)
    assert len(pending) == 1


def test_task_queue_update_status():
    q = TaskQueue()
    item = q.enqueue("s1", "fix")
    assert q.update_status(item.item_id, "RUNNING")
    assert item.status == "RUNNING"


def test_task_queue_remove():
    q = TaskQueue()
    item = q.enqueue("s1", "fix")
    assert q.remove(item.item_id)
    assert q.get(item.item_id) is None


def test_task_queue_clear_completed():
    q = TaskQueue()
    i1 = q.enqueue("s1", "fix")
    i2 = q.enqueue("s2", "fix")
    q.update_status(i1.item_id, "COMPLETED")
    assert q.clear_completed() == 1
    assert q.get(i1.item_id) is None
    assert q.get(i2.item_id) is not None


# ---------------------------------------------------------------------------
# Evaluation Harness tests
# ---------------------------------------------------------------------------

def test_golden_task_defaults():
    t = GoldenTask()
    assert t.tags == []


def test_eval_result_defaults():
    r = EvalResult()
    assert not r.passed


def test_eval_suite_result_defaults():
    s = EvalSuiteResult()
    assert s.total == 0
    assert s.pass_rate == 1.0


def test_eval_suite_result_pass_rate():
    s = EvalSuiteResult(total=10, passed=7, failed=3)
    assert s.pass_rate == 0.7


def test_evaluation_harness_register():
    h = EvaluationHarness()
    t = GoldenTask(task_id="t1", description="fix parser")
    h.register_task(t)
    assert h.get_task("t1") is t


def test_evaluation_harness_list_tasks():
    h = EvaluationHarness()
    h.register_task(GoldenTask(task_id="t1", tags=["core"]))
    h.register_task(GoldenTask(task_id="t2", tags=["core"]))
    assert len(h.list_tasks(tag="core")) == 2


def test_evaluation_harness_run_suite():
    h = EvaluationHarness()
    h.register_task(GoldenTask(task_id="t1"))
    h.register_task(GoldenTask(task_id="t2"))
    suite = h.run_suite()
    assert suite.total == 2
    assert suite.passed == 2


def test_evaluation_harness_run_suite_with_evaluator():
    h = EvaluationHarness()
    h.register_task(GoldenTask(task_id="t1"))

    def evaluator(task):
        return EvalResult(task_id=task.task_id, passed=False, actual_outcome="failed")

    suite = h.run_suite(evaluator=evaluator)
    assert suite.total == 1
    assert suite.passed == 0


def test_evaluation_harness_latest_suite():
    h = EvaluationHarness()
    h.register_task(GoldenTask(task_id="t1"))
    s1 = h.run_suite()
    s2 = h.run_suite()
    assert h.latest_suite() is s2


def test_quality_scorecard():
    q = QualityScorecard()
    q.set_score("reliability", 0.85)
    q.set_score("safety", 0.95)
    assert q.get_score("reliability") == 0.85
    assert 0.89 < q.average() < 0.91


def test_quality_scorecard_clamps():
    q = QualityScorecard()
    q.set_score("metric", 1.5)
    assert q.get_score("metric") == 1.0
    q.set_score("metric", -0.5)
    assert q.get_score("metric") == 0.0


# ---------------------------------------------------------------------------
# Documentation Sync tests
# ---------------------------------------------------------------------------

def test_doc_drift_defaults():
    d = DocDrift()
    assert d.severity == "info"


def test_doc_sync_checker_all_pass():
    c = DocSyncChecker()
    checks = [
        {"location": "README.md", "expected": "install", "actual": "install"},
    ]
    result = c.check(checks)
    assert result.passed
    assert result.total_checks == 1


def test_doc_sync_checker_drift():
    c = DocSyncChecker()
    checks = [
        {"location": "README.md", "expected": "install", "actual": "install now"},
    ]
    result = c.check(checks)
    assert not result.passed
    assert len(result.drifts) == 1


def test_schema_doc_checker():
    c = SchemaDocChecker()
    fields = [{"name": "field1"}, {"name": "field2"}]
    mismatches = c.check(fields, ["field1"])
    assert len(mismatches) == 1
    assert "field2" in mismatches[0]


def test_schema_doc_checker_reverse():
    c = SchemaDocChecker()
    fields = [{"name": "field1"}]
    mismatches = c.check(fields, ["field1", "field2"])
    assert len(mismatches) == 1


# ---------------------------------------------------------------------------
# Local Model Runtime Profile tests
# ---------------------------------------------------------------------------

def test_runtime_profile_defaults():
    p = RuntimeProfile()
    assert p.profile_id == RP_CPU_ONLY_SAFE
    assert p.max_context_tokens == 4096


def test_default_profiles_exist():
    assert RP_CPU_ONLY_SAFE in DEFAULT_PROFILES
    assert RP_SMALL_GPU_8GB in DEFAULT_PROFILES
    assert RP_BALANCED_LOCAL in DEFAULT_PROFILES
    assert RP_HOSTED_FALLBACK in DEFAULT_PROFILES


def test_model_resource_budget_default():
    b = ModelResourceBudget()
    assert b.profile.profile_id == RP_CPU_ONLY_SAFE


def test_model_resource_budget_switch():
    b = ModelResourceBudget()
    assert b.switch_profile(RP_SMALL_GPU_8GB)
    assert b.profile.profile_id == RP_SMALL_GPU_8GB
    assert not b.switch_profile("nonexistent")


def test_model_resource_budget_headroom():
    b = ModelResourceBudget(DEFAULT_PROFILES[RP_CPU_ONLY_SAFE])
    assert b.headroom(100) == 2048 - 100


def test_model_resource_budget_max_context():
    b = ModelResourceBudget(DEFAULT_PROFILES[RP_HOSTED_FALLBACK])
    assert b.max_context_for_task("IMPLEMENT_PATCH") == 16384


# ---------------------------------------------------------------------------
# Monitoring / Observability tests
# ---------------------------------------------------------------------------

def test_audit_event_defaults():
    e = AuditEvent()
    assert e.event_type == ""


def test_audit_log_log():
    log = AuditLog()
    e = log.log("patch_applied", "s1", "patcher", "patch applied")
    assert e.event_id.startswith("evt-")
    assert e.event_type == "patch_applied"


def test_audit_log_get_by_session():
    log = AuditLog()
    log.log("a", "s1", "c1", "msg1")
    log.log("b", "s2", "c2", "msg2")
    assert len(log.get_by_session("s1")) == 1


def test_audit_log_get_by_type():
    log = AuditLog()
    log.log("error", "s1", "c1", "err1")
    log.log("info", "s2", "c2", "info1")
    assert len(log.get_by_type("error")) == 1


def test_audit_log_clear():
    log = AuditLog()
    log.log("a", "s1", "c1", "msg")
    log.clear()
    assert len(log.list_all()) == 0


def test_session_inspector():
    log = AuditLog()
    log.log("failure", "s1", "worker", "model failed")
    ins = SessionInspector(audit_log=log)
    result = ins.inspect_session("s1")
    assert result["event_count"] == 1


def test_session_inspector_last_failure():
    log = AuditLog()
    log.log("info", "s1", "c1", "ok")
    log.log("failure", "s1", "c1", "fail msg")
    ins = SessionInspector(audit_log=log)
    last = ins.last_failure("s1")
    assert last is not None
    assert last.message == "fail msg"


def test_session_inspector_no_failure():
    log = AuditLog()
    log.log("info", "s1", "c1", "ok")
    ins = SessionInspector(audit_log=log)
    assert ins.last_failure("s1") is None


# ---------------------------------------------------------------------------
# Final System Acceptance tests
# ---------------------------------------------------------------------------

def test_acceptance_check_defaults():
    c = AcceptanceCheck()
    report = c.run_all()
    assert report.total == 19
    assert report.passed > 0
    assert report.skipped == 0


def test_acceptance_check_set():
    c = AcceptanceCheck()
    c.set_result("patch_execution", "PASS")
    result = c.get_result("patch_execution")
    assert result is not None
    assert result.status == "PASS"


def test_acceptance_check_summary():
    c = AcceptanceCheck()
    c.set_result("patch_execution", "PASS")
    c.set_result("rollback", "PASS")
    summary = c.summary()
    assert summary["total"] == 2
    assert summary["passed"] == 2
    assert summary["failed"] == 0


# ---------------------------------------------------------------------------
# End-to-end integration: orchestrator + real hooks + acceptance check
# ---------------------------------------------------------------------------

def test_orchestration_session_defaults():
    s = OrchestrationSession()
    assert s.session_id == ""
    assert s.status == "CREATED"


def test_acceptance_with_real_check_integration():
    c = AcceptanceCheck()
    report = c.run_all()
    assert report.total == 19
    assert report.passed >= 17
    assert report.skipped == 0
    check_names = {r.check_name for r in report.checks}
    assert "fresh_clone_install" in check_names
    assert "patch_execution" in check_names
    assert "schema_validation" in check_names
    for r in report.checks:
        if r.status == AC_CHECK_PASS:
            assert r.details, f"Check {r.check_name} passed but has no details"


def test_packaging_integration():
    from agentx_evolve.packaging.packaging_checker import PackagingChecker
    checker = PackagingChecker()
    c = checker.run_check()
    assert c.check_id.startswith("pkg-")
    assert len(c.dep_groups_defined) > 0
    for check in c.checks:
        if check.check_name.startswith("cmd_"):
            assert check.status in ("PASS", "FAIL"), f"{check.check_name}: unexpected {check.status}"


def test_backup_persistence_integration(tmp_path):
    from agentx_evolve.backup.backup_recovery import BackupManager, BC_AUDIT_HISTORY, BK_COMPLETED
    backup_dir = tmp_path / "backups"
    bak_file = tmp_path / "test.bak"
    bak_file.write_text("backup content")
    mgr = BackupManager(backup_dir=str(backup_dir))
    r = mgr.create_backup(BC_AUDIT_HISTORY, source_paths=["/tmp/test.log"])
    mgr.complete_backup(r.backup_id, backup_paths=[str(bak_file)],
                        checksum="abc123", size_bytes=512)
    assert r.status == BK_COMPLETED
    assert (backup_dir / "backups.jsonl").exists()
    mgr2 = BackupManager(backup_dir=str(backup_dir))
    assert mgr2.get_backup(r.backup_id) is not None
    ok, msg = mgr2.can_restore(r.backup_id)
    assert ok is True
