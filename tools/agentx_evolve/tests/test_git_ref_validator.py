import pytest
from agentx_evolve.git.git_ref_validator import (
    is_protected_branch, is_valid_branch_name, validate_ref,
)
from agentx_evolve.git.git_models import (
    REF_KIND_BRANCH, REF_KIND_TAG, REF_KIND_REMOTE,
)


class TestIsProtectedBranch:
    def test_main_is_protected(self):
        assert is_protected_branch("main")

    def test_master_is_protected(self):
        assert is_protected_branch("master")

    def test_release_is_protected(self):
        assert is_protected_branch("release")

    def test_production_is_protected(self):
        assert is_protected_branch("production")

    def test_stable_is_protected(self):
        assert is_protected_branch("stable")

    def test_develop_is_protected(self):
        assert is_protected_branch("develop")

    def test_feature_branch_not_protected(self):
        assert not is_protected_branch("feature/my-feature")

    def test_refs_heads_prefix_works(self):
        assert is_protected_branch("refs/heads/main")

    def test_random_name_not_protected(self):
        assert not is_protected_branch("random-branch")

    def test_staging_is_protected(self):
        assert is_protected_branch("staging")


class TestIsValidBranchName:
    def test_valid_name(self):
        assert is_valid_branch_name("feature/new-feature")

    def test_empty_name_invalid(self):
        assert not is_valid_branch_name("")

    def test_starts_with_dash_invalid(self):
        assert not is_valid_branch_name("-branch")

    def test_double_dot_invalid(self):
        assert not is_valid_branch_name("my..branch")

    def test_at_brace_invalid(self):
        assert not is_valid_branch_name("branch@{1}")

    def test_ends_with_lock_invalid(self):
        assert not is_valid_branch_name("branch.lock")

    def test_ends_with_slash_invalid(self):
        assert not is_valid_branch_name("branch/")

    def test_ends_with_dot_invalid(self):
        assert not is_valid_branch_name("branch.")

    def test_double_slash_invalid(self):
        assert not is_valid_branch_name("branch//sub")

    def test_control_chars_invalid(self):
        assert not is_valid_branch_name("branch\x00name")
        assert not is_valid_branch_name("branch\x7fname")

    def test_full_hex_string_invalid(self):
        assert not is_valid_branch_name("a" * 40)

    def test_uppercase_hex_string_invalid(self):
        assert not is_valid_branch_name("A" * 40)

    def test_valid_complex_name(self):
        assert is_valid_branch_name("JIRA-123_feature/some-thing")


class TestValidateRef:
    def test_valid_branch_ref(self):
        result = validate_ref("feature/new", "/tmp", ref_kind=REF_KIND_BRANCH)
        assert result.is_valid
        assert result.ref_kind == REF_KIND_BRANCH
        assert result.normalized_ref == "feature/new"

    def test_protected_branch_ref(self):
        result = validate_ref("main", "/tmp", ref_kind=REF_KIND_BRANCH)
        assert result.is_valid
        assert result.is_protected

    def test_invalid_branch_name(self):
        result = validate_ref("", "/tmp", ref_kind=REF_KIND_BRANCH)
        assert not result.is_valid

    def test_tag_ref_kind_blocked(self):
        result = validate_ref("v1.0", "/tmp", ref_kind=REF_KIND_TAG)
        assert not result.is_valid
        assert "blocked" in result.message.lower()

    def test_remote_ref_kind_blocked(self):
        result = validate_ref("origin/main", "/tmp", ref_kind=REF_KIND_REMOTE)
        assert not result.is_valid
        assert "blocked" in result.message.lower()

    def test_result_has_raw_ref(self):
        result = validate_ref("main", "/tmp")
        assert result.raw_ref == "main"

    def test_result_id_starts_with_grvr(self):
        result = validate_ref("main", "/tmp")
        assert result.result_id.startswith("grvr-")

    def test_has_timestamp(self):
        result = validate_ref("main", "/tmp")
        assert "T" in result.timestamp
