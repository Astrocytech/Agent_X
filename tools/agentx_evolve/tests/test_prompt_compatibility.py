import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import (
    PromptVersion, PromptContract, PromptDiffRecord,
    COMPATIBILITY_COMPATIBLE, COMPATIBILITY_BREAKING,
    COMPATIBILITY_REQUIRES_MIGRATION,
    sha256_text,
)
from agentx_evolve.prompts.prompt_compatibility import (
    check_prompt_compatibility, classify_prompt_change, requires_migration,
)


class TestCheckPromptCompatibility:
    def test_compatible_change_allows_activation(self):
        contract = PromptContract(prompt_contract_id="pc-001")
        old = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="## Section\nsame content",
            prompt_body_sha256="abc", change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="1.1", prompt_body="## Section\nsame content",
            prompt_body_sha256="def", change_summary="no change",
        )
        diff = check_prompt_compatibility(old, new, contract)
        assert diff.compatibility_result == COMPATIBILITY_COMPATIBLE

    def test_breaking_change_detected(self):
        contract = PromptContract(prompt_contract_id="pc-001")
        old = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="## Section\nold content",
            prompt_body_sha256="abc", change_summary="initial",
            breaking_change=False,
        )
        new = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="2.0", prompt_body="## Section\nnew content with required output change",
            prompt_body_sha256="def", change_summary="required output changed",
            breaking_change=True,
        )
        diff = check_prompt_compatibility(old, new, contract)
        assert diff.compatibility_result in (
            COMPATIBILITY_BREAKING, COMPATIBILITY_REQUIRES_MIGRATION
        )

    def test_output_contract_change_is_breaking(self):
        contract = PromptContract(prompt_contract_id="pc-001")
        old = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="## Section\nold output format",
            prompt_body_sha256=sha256_text("## Section\nold output format"),
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="2.0", prompt_body="## Section\nnew output format changed",
            prompt_body_sha256=sha256_text("## Section\nnew output format changed"),
            change_summary="required output field changed",
            breaking_change=True,
        )
        diff = check_prompt_compatibility(old, new, contract)
        assert diff.compatibility_result != COMPATIBILITY_COMPATIBLE


class TestClassifyPromptChange:
    def test_requires_migration_detected(self):
        record = PromptDiffRecord(
            diff_id="pd-001",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            summary="changed section",
            changed_sections=["## Section"],
            compatibility_result=COMPATIBILITY_REQUIRES_MIGRATION,
        )
        assert requires_migration(record) is True

    def test_compatible_does_not_require_migration(self):
        record = PromptDiffRecord(
            diff_id="pd-002",
            from_prompt_version_id="pv-001",
            to_prompt_version_id="pv-002",
            summary="no change",
            compatibility_result=COMPATIBILITY_COMPATIBLE,
        )
        assert requires_migration(record) is False
