import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptContract, PromptVersion, PromptRegistry, PromptRegistrySnapshot,
    PromptInputContract, PromptOutputContract, PromptSafetyRule,
    PromptProvenance, PromptDiffRecord, PromptMigrationRecord,
    PromptRuntimeBinding, PromptWorkerPayload, PromptPermissionDecision,
    PromptAuditEvent,
    PROMPT_STATUS_DRAFT, PROMPT_STATUS_ACTIVE, ALL_PROMPT_STATUSES,
    PROMPT_TYPE_TASK, ALL_PROMPT_TYPES,
    COMPATIBILITY_COMPATIBLE, ALL_COMPATIBILITY_RESULTS,
    PROMPT_DECISION_ALLOW, ALL_PROMPT_DECISIONS,
    PROMPT_SAFETY_MEDIUM, ALL_SAFETY_LEVELS,
    MIGRATION_STATUS_REQUIRED, ALL_MIGRATION_STATUSES,
    utc_now_iso, new_id, sha256_text, sha256_dict, redact_prompt_text, to_dict,
)


class TestConstants:
    def test_all_prompt_statuses(self):
        assert PROMPT_STATUS_DRAFT in ALL_PROMPT_STATUSES
        assert PROMPT_STATUS_ACTIVE in ALL_PROMPT_STATUSES
        assert len(ALL_PROMPT_STATUSES) == 5

    def test_all_prompt_types(self):
        assert PROMPT_TYPE_TASK in ALL_PROMPT_TYPES
        assert len(ALL_PROMPT_TYPES) == 9

    def test_all_compatibility_results(self):
        assert COMPATIBILITY_COMPATIBLE in ALL_COMPATIBILITY_RESULTS
        assert len(ALL_COMPATIBILITY_RESULTS) == 4

    def test_all_prompt_decisions(self):
        assert PROMPT_DECISION_ALLOW in ALL_PROMPT_DECISIONS
        assert len(ALL_PROMPT_DECISIONS) == 5

    def test_all_safety_levels(self):
        assert PROMPT_SAFETY_MEDIUM in ALL_SAFETY_LEVELS
        assert len(ALL_SAFETY_LEVELS) == 4

    def test_all_migration_statuses(self):
        assert MIGRATION_STATUS_REQUIRED in ALL_MIGRATION_STATUSES
        assert len(ALL_MIGRATION_STATUSES) == 5


class TestDataclasses:
    def test_prompt_contract_instantiates(self):
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test")
        assert c.prompt_contract_id == "pc-001"
        assert c.schema_version == "1.0"
        assert c.status == PROMPT_STATUS_DRAFT

    def test_prompt_version_instantiates(self):
        v = PromptVersion(prompt_version_id="pv-001", prompt_contract_id="pc-001")
        assert v.prompt_version_id == "pv-001"
        assert v.schema_id == "prompt_version.schema.json"

    def test_prompt_registry_instantiates(self):
        r = PromptRegistry(registry_id="pr-001")
        assert r.registry_id == "pr-001"
        assert r.source_component == "PromptRegistry"

    def test_prompt_registry_snapshot_instantiates(self):
        s = PromptRegistrySnapshot(snapshot_id="prs-001", registry_id="pr-001")
        assert s.snapshot_id == "prs-001"

    def test_prompt_input_contract_instantiates(self):
        ic = PromptInputContract(input_contract_id="ic-001")
        assert ic.input_contract_id == "ic-001"

    def test_prompt_output_contract_instantiates(self):
        oc = PromptOutputContract(output_contract_id="oc-001")
        assert oc.output_contract_id == "oc-001"

    def test_prompt_safety_rule_instantiates(self):
        sr = PromptSafetyRule(safety_rule_id="sr-001", name="test")
        assert sr.name == "test"

    def test_prompt_provenance_instantiates(self):
        p = PromptProvenance(provenance_id="pp-001", prompt_contract_id="pc-001")
        assert p.provenance_id == "pp-001"

    def test_prompt_diff_record_instantiates(self):
        d = PromptDiffRecord(diff_id="pd-001", from_prompt_version_id="pv-001", to_prompt_version_id="pv-002")
        assert d.diff_id == "pd-001"

    def test_prompt_migration_record_instantiates(self):
        m = PromptMigrationRecord(migration_id="pm-001")
        assert m.migration_id == "pm-001"

    def test_prompt_runtime_binding_instantiates(self):
        b = PromptRuntimeBinding(binding_id="rb-001")
        assert b.binding_id == "rb-001"

    def test_prompt_worker_payload_instantiates(self):
        w = PromptWorkerPayload(payload_id="pwp-001", binding_id="rb-001")
        assert w.payload_id == "pwp-001"

    def test_prompt_permission_decision_instantiates(self):
        p = PromptPermissionDecision(decision_id="ppd-001")
        assert p.decision_id == "ppd-001"

    def test_prompt_audit_event_instantiates(self):
        a = PromptAuditEvent(audit_id="pa-001", event_type="TEST")
        assert a.audit_id == "pa-001"


class TestHelpers:
    def test_utc_now_iso_returns_string(self):
        result = utc_now_iso()
        assert isinstance(result, str)
        assert "T" in result

    def test_new_id_has_prefix(self):
        result = new_id("test")
        assert result.startswith("test-")

    def test_sha256_text_is_deterministic(self):
        h1 = sha256_text("hello world")
        h2 = sha256_text("hello world")
        assert h1 == h2
        assert len(h1) == 64

    def test_sha256_text_differs_for_different_input(self):
        h1 = sha256_text("hello")
        h2 = sha256_text("world")
        assert h1 != h2

    def test_sha256_dict_is_deterministic(self):
        d = {"b": 2, "a": 1}
        h1 = sha256_dict(d)
        h2 = sha256_dict(d)
        assert h1 == h2

    def test_sha256_dict_sorts_keys(self):
        h1 = sha256_dict({"b": 2, "a": 1})
        h2 = sha256_dict({"a": 1, "b": 2})
        assert h1 == h2

    def test_redact_prompt_text_short(self):
        text = "short text"
        result = redact_prompt_text(text, max_chars=100)
        assert result == text

    def test_redact_prompt_text_long(self):
        text = "x" * 5000
        result = redact_prompt_text(text, max_chars=100)
        assert "[REDACTED" in result
        assert len(result) < len(text)

    def test_to_dict_with_dataclass(self):
        c = PromptContract(prompt_contract_id="pc-001", prompt_name="test")
        d = to_dict(c)
        assert d["prompt_contract_id"] == "pc-001"
        assert d["schema_version"] == "1.0"
