import os

from agentx_evolve.runtime.config import (
    ConfigResolver, RuntimeConfig,
    BUILTIN_PROVIDER, BUILTIN_MODEL, BUILTIN_TIMEOUT,
)


class TestConfigDefaults:
    def test_builtin_defaults(self):
        resolver = ConfigResolver()
        config = resolver.resolve([])
        assert config.provider == BUILTIN_PROVIDER
        assert config.model == BUILTIN_MODEL
        assert config.timeout_seconds == BUILTIN_TIMEOUT
        assert config.json is False
        assert config.mock is True
        assert config.run_root == ".agentx-init/runs"

    def test_mock_flag_sets_provider(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--mock"])
        assert config.mock is True
        assert config.provider == "mock"

    def test_json_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--json"])
        assert config.json is True

    def test_once_message(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--once", "Say READY"])
        assert config.once_message == "Say READY"

    def test_provider_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--provider", "opencode"])
        assert config.provider == "opencode"

    def test_model_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--model", "custom/model"])
        assert config.model == "custom/model"

    def test_run_root_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--run-root", "/tmp/my_runs"])
        assert config.run_root == "/tmp/my_runs"

    def test_timeout_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--timeout", "120"])
        assert config.timeout_seconds == 120

    def test_dry_run_flag(self):
        resolver = ConfigResolver()
        config = resolver.resolve(["--dry-run"])
        assert config.dry_run is True

    def test_cli_overrides_env(self):
        os.environ["AGENTX_PROVIDER"] = "opencode"
        os.environ["AGENTX_MODEL"] = "opencode/big-pickle"
        resolver = ConfigResolver()
        config = resolver.resolve(["--provider", "mock"])
        assert config.provider == "mock"
        assert config.model == "opencode/big-pickle"
        del os.environ["AGENTX_PROVIDER"]
        del os.environ["AGENTX_MODEL"]

    def test_env_vars(self):
        os.environ["AGENTX_TIMEOUT_SECONDS"] = "300"
        resolver = ConfigResolver()
        config = resolver.resolve([])
        assert config.timeout_seconds == 300
        del os.environ["AGENTX_TIMEOUT_SECONDS"]

    def test_redacted_dict_hides_secrets(self):
        config = RuntimeConfig(opencode_api_key="sk-secret-123")
        d = config.redacted_dict()
        assert d["opencode_api_key"] == "***REDACTED***"
        assert "sk-secret" not in str(d)
