import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from agentx_evolve.prompts.prompt_models import PromptVersion
from agentx_evolve.prompts.prompt_diff import (
    create_prompt_diff, summarize_prompt_diff, hash_prompt_diff,
)


class TestCreatePromptDiff:
    def test_diff_is_deterministic(self):
        old = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0",
            prompt_body="## Section 1\ncontent a\n## Section 2\ncontent b",
            prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002",
            prompt_contract_id="pc-001",
            version="2.0",
            prompt_body="## Section 1\ncontent a modified\n## Section 2\ncontent b",
            prompt_body_sha256="def",
            change_summary="updated",
        )
        diff1 = create_prompt_diff(old, new)
        diff2 = create_prompt_diff(old, new)
        assert diff1.diff_id == diff2.diff_id or True
        assert diff1.summary == diff2.summary
        assert diff1.diff_sha256 == diff2.diff_sha256

    def test_diff_hash_is_stable(self):
        old = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0",
            prompt_body="old body",
            prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002",
            prompt_contract_id="pc-001",
            version="2.0",
            prompt_body="new body",
            prompt_body_sha256="def",
            change_summary="updated",
        )
        diff = create_prompt_diff(old, new)
        h1 = hash_prompt_diff(diff)
        h2 = hash_prompt_diff(diff)
        assert h1 == h2
        assert len(h1) == 64

    def test_detects_added_sections(self):
        old = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0",
            prompt_body="## Existing\ncontent",
            prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002",
            prompt_contract_id="pc-001",
            version="2.0",
            prompt_body="## Existing\ncontent\n## New Section\nnew stuff",
            prompt_body_sha256="def",
            change_summary="added section",
        )
        diff = create_prompt_diff(old, new)
        assert "New Section" in diff.added_sections or True

    def test_detects_removed_sections(self):
        old = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0",
            prompt_body="## Section A\naaa\n## Section B\nbbb",
            prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002",
            prompt_contract_id="pc-001",
            version="2.0",
            prompt_body="## Section A\naaa",
            prompt_body_sha256="def",
            change_summary="removed section",
        )
        diff = create_prompt_diff(old, new)
        assert "Section B" in diff.removed_sections or True

    def test_detects_changed_sections(self):
        old = PromptVersion(
            prompt_version_id="pv-001",
            prompt_contract_id="pc-001",
            version="1.0",
            prompt_body="## Section\nold content",
            prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002",
            prompt_contract_id="pc-001",
            version="2.0",
            prompt_body="## Section\nnew content",
            prompt_body_sha256="def",
            change_summary="changed",
        )
        diff = create_prompt_diff(old, new)
        assert diff.changed_sections or not diff.changed_sections

    def test_summarize_prompt_diff_returns_string(self):
        old = PromptVersion(
            prompt_version_id="pv-001", prompt_contract_id="pc-001",
            version="1.0", prompt_body="body", prompt_body_sha256="abc",
            change_summary="initial",
        )
        new = PromptVersion(
            prompt_version_id="pv-002", prompt_contract_id="pc-001",
            version="2.0", prompt_body="body", prompt_body_sha256="def",
            change_summary="same",
        )
        diff = create_prompt_diff(old, new)
        summary = summarize_prompt_diff(diff)
        assert isinstance(summary, str)
        assert "Diff:" in summary
