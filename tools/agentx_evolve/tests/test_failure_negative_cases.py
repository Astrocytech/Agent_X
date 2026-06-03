import pytest


def test_no_llm_imports():
    import agentx_evolve.recovery as R
    mods = dir(R)
    for name in mods:
        if "llm" in name.lower():
            pytest.fail(f"LLM-related name found: {name}")
        if name == "model" or name == "Model":
            pytest.fail(f"Model import found: {name}")


def test_no_network_imports():
    import sys
    for modname in list(sys.modules.keys()):
        if "agentx_evolve.recovery" in modname:
            mod = sys.modules[modname]
            if mod is None:
                continue
            try:
                src = getattr(mod, "__file__", "") or ""
            except Exception:
                continue
            if "requests" in src or "urllib" in src or "http" in src:
                pytest.fail(f"Network import in {modname}")


def test_no_patch_execution_imports():
    import agentx_evolve.recovery.failure_models as fm
    import agentx_evolve.recovery.failure_taxonomy as ft
    import agentx_evolve.recovery.recovery_policy as rp
    import agentx_evolve.recovery.safe_mode_triggers as smt
    import agentx_evolve.recovery.recovery_decider as rd
    import agentx_evolve.recovery.recovery_playbook as rpl
    for mod in [fm, ft, rp, smt, rd, rpl]:
        src = getattr(mod, "__file__", "")
        if "patch_execution" in src or "patch_applier" in src or "rollback_manager" in src:
            pytest.fail(f"Patch execution import in {mod.__name__}")


def test_no_rollback_execution():
    from agentx_evolve.recovery.recovery_policy import select_recovery_actions
    from agentx_evolve.recovery.failure_models import FailureRecord, ACTION_ROLLBACK
    f = FailureRecord(failure_id="t", failure_class="PATCH_APPLY_FAILED", severity="HIGH", requires_recovery=True)
    actions = select_recovery_actions(f, {"mutation_started": True, "rollback_available": True})
    types = {a.action_type for a in actions}
    assert ACTION_ROLLBACK in types


def test_no_shell_execution():
    import agentx_evolve.recovery.failure_evidence as fe
    import agentx_evolve.recovery.recovery_decider as rd
    for mod in [fe, rd]:
        src = getattr(mod, "__file__", "")
        with open(src) as f:
            content = f.read()
        assert "subprocess" not in content, f"subprocess in {mod.__name__}"
        assert "os.system" not in content, f"os.system in {mod.__name__}"


def test_no_source_mutation():
    import agentx_evolve.recovery.failure_evidence as fe
    import agentx_evolve.recovery.failure_models as fm
    for mod in [fe, fm]:
        src = getattr(mod, "__file__", "")
        with open(src) as f:
            content = f.read()
        assert "safe_write_file" not in content, f"safe_write_file in {mod.__name__}"
        assert "safe_exact_edit" not in content, f"safe_exact_edit in {mod.__name__}"


def test_critical_failure_cannot_continue():
    from agentx_evolve.recovery.recovery_decider import decide_recovery
    from agentx_evolve.recovery.failure_models import FailureRecord, SEVERITY_CRITICAL
    f = FailureRecord(failure_id="t", failure_class="ROLLBACK_FAILED", severity=SEVERITY_CRITICAL, requires_recovery=True)
    d = decide_recovery(f)
    assert d.continue_session_allowed is False


def test_unknown_failure_cannot_be_silent_success():
    from agentx_evolve.recovery.failure_taxonomy import classify_failure
    result = classify_failure({})
    assert result.failure_class == "UNKNOWN_FAILURE"
    assert result.requires_human_review is True
