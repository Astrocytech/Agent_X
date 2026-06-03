from pathlib import Path
from agentx_evolve.security.sandbox_policy import (
    default_sandbox_policy, load_sandbox_policy_from_dict,
    merge_sandbox_policy, is_runtime_path, is_protected_path, is_l0_path,
)
from agentx_evolve.security.security_models import SandboxPolicy


class TestDefaultSandboxPolicy:
    def test_defaults(self):
        policy = default_sandbox_policy(Path("/tmp/repo"))
        assert policy.repo_root == Path("/tmp/repo").resolve().as_posix()
        assert policy.source_write_allowed is False
        assert policy.runtime_write_allowed is True
        assert policy.network_allowed is False
        assert policy.shell_allowed is False
        assert policy.max_file_size_bytes == 1048576
        assert "L0/" in policy.protected_paths
        assert ".agentx-init/" in policy.allowlisted_write_paths
        assert "L0/" in policy.blocked_write_paths


class TestLoadSandboxPolicyFromDict:
    def test_empty(self):
        policy = load_sandbox_policy_from_dict({})
        assert isinstance(policy, SandboxPolicy)
        assert policy.policy_id != ""

    def test_with_values(self):
        data = {
            "policy_id": "pol-1",
            "repo_root": "/custom/repo",
            "source_write_allowed": True,
            "max_file_size_bytes": 512000,
            "redact_secret_patterns": ["AKIA"],
        }
        policy = load_sandbox_policy_from_dict(data, repo_root=Path("/other/repo"))
        assert policy.source_write_allowed is True
        assert policy.repo_root == Path("/other/repo").resolve().as_posix()
        assert policy.redact_secret_patterns == ["AKIA"]

    def test_unknown_fields_ignored(self):
        policy = load_sandbox_policy_from_dict({"nonexistent_field": "value"})
        assert not hasattr(policy, "nonexistent_field")


class TestMergeSandboxPolicy:
    def test_merge_overrides(self):
        base = default_sandbox_policy(Path("/repo"))
        override = {"source_write_allowed": True, "shell_allowed": True}
        merged = merge_sandbox_policy(base, override)
        assert merged.source_write_allowed is True
        assert merged.shell_allowed is True

    def test_merge_appends_protected_paths(self):
        base = default_sandbox_policy(Path("/repo"))
        override = {"protected_paths": ["secrets/"]}
        merged = merge_sandbox_policy(base, override)
        assert "L0/" in merged.protected_paths
        assert "secrets/" in merged.protected_paths

    def test_merge_appends_blocked_write_paths(self):
        base = default_sandbox_policy(Path("/repo"))
        override = {"blocked_write_paths": ["extra_blocked/"]}
        merged = merge_sandbox_policy(base, override)
        assert "extra_blocked/" in merged.blocked_write_paths

    def test_merge_preserves_base(self):
        base = default_sandbox_policy(Path("/repo"))
        override = {"source_write_allowed": True}
        merged = merge_sandbox_policy(base, override)
        assert merged.runtime_write_allowed == base.runtime_write_allowed
        assert merged.network_allowed == base.network_allowed


class TestIsRuntimePath:
    def test_path_under_runtime_root(self, tmp_path):
        repo_root = tmp_path / "repo"
        repo_root.mkdir()
        policy = default_sandbox_policy(repo_root)
        runtime_file = repo_root / ".agentx-init" / "state.json"
        runtime_file.parent.mkdir(parents=True)
        runtime_file.write_text("{}")
        assert is_runtime_path(runtime_file, repo_root, policy) is True


class TestIsProtectedPath:
    def test_protected_paths(self):
        policy = SandboxPolicy(protected_paths=["L0/", "core/"])
        assert is_protected_path("L0/something.py", policy) is True
        assert is_protected_path("L0", policy) is True
        assert is_protected_path("core/config.py", policy) is True
        assert is_protected_path("src/main.py", policy) is False

    def test_trailing_slash_normalized(self):
        policy = SandboxPolicy(protected_paths=["L0"])
        assert is_protected_path("L0/", policy) is True


class TestIsL0Path:
    def test_l0_paths(self):
        assert is_l0_path("L0/file.py") is True
        assert is_l0_path("L0") is True
        assert is_l0_path("src/file.py") is False
        assert is_l0_path("L0/") is True
