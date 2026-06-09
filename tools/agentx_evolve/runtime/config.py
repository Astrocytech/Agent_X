from __future__ import annotations
import os
from dataclasses import dataclass, field
from typing import Any

BUILTIN_PROVIDER = "opencode"
BUILTIN_MODEL = "big-pickle"
BUILTIN_RUN_ROOT = ".agentx-init/runs"
BUILTIN_TIMEOUT = 0
BUILTIN_JSON = False
BUILTIN_MOCK = False
BUILTIN_MODE = "plan"
BUILTIN_DRY_RUN = False


@dataclass
class RuntimeConfig:
    provider: str = BUILTIN_PROVIDER
    model: str = BUILTIN_MODEL
    run_root: str = BUILTIN_RUN_ROOT
    timeout_seconds: int = BUILTIN_TIMEOUT
    json: bool = BUILTIN_JSON
    mock: bool = BUILTIN_MOCK
    mode: str = BUILTIN_MODE
    dry_run: bool = BUILTIN_DRY_RUN
    command: str = ""
    opencode_base_url: str = "http://127.0.0.1:14096"
    opencode_api_key: str = ""
    api_base_url: str = "http://127.0.0.1:11434/v1"
    api_key: str = ""
    once_message: str = ""
    concept_file: str = ""
    agent_name: str = ""
    opencode_session_id: str = ""
    session_id: str = ""
    agent_dest: str = ""
    agent_dir: str = ""
    dest: str = ""
    extra: dict[str, Any] = field(default_factory=dict)

    SECRET_KEYS = {"opencode_api_key", "api_key"}

    def redacted_dict(self) -> dict[str, Any]:
        d = self.to_dict()
        for key in self.SECRET_KEYS:
            if key in d and d[key]:
                d[key] = "***REDACTED***"
        return d

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "model": self.model,
            "run_root": self.run_root,
            "timeout_seconds": self.timeout_seconds,
            "json": self.json,
            "mock": self.mock,
            "mode": self.mode,
            "dry_run": self.dry_run,
            "command": self.command,
            "opencode_base_url": self.opencode_base_url,
            "opencode_api_key": self.opencode_api_key,
            "opencode_session_id": self.opencode_session_id,
            "api_base_url": self.api_base_url,
            "api_key": self.api_key,
            "session_id": self.session_id,
            "once_message": self.once_message,
            "concept_file": self.concept_file,
            "agent_name": self.agent_name,
            "agent_dest": self.agent_dest,
            "agent_dir": self.agent_dir,
            "dest": self.dest,
        }


class ConfigResolver:
    def resolve(self, argv: list[str] | None = None) -> RuntimeConfig:
        args = self._parse_argv(argv or [])
        config = self._from_env()
        self._apply_args(config, args)
        config.provider = config.mock and "mock" or config.provider
        return config

    KNOWN_FLAGS = {
        "--json", "--mock", "--dry-run",
        "--once", "--provider", "--model", "--run-root", "--timeout",
        "--concept-file", "--mode",
        "--name", "--dest", "--agent-dir", "--command",
        "--session-id", "--api-base-url", "--api-key",
    }

    def _parse_argv(self, argv: list[str]) -> dict[str, Any]:
        args: dict[str, Any] = {}
        it = iter(argv)
        for token in it:
            if token == "--json":
                args["json"] = True
            elif token == "--mock":
                args["mock"] = True
            elif token == "--dry-run":
                args["dry_run"] = True
            elif token == "--once":
                args["once_message"] = next(it, "")
            elif token == "--provider":
                args["provider"] = next(it, "")
            elif token == "--model":
                args["model"] = next(it, "")
            elif token == "--run-root":
                args["run_root"] = next(it, "")
            elif token == "--timeout":
                args["timeout_seconds"] = int(next(it, "0"))
            elif token == "--concept-file":
                args["concept_file"] = next(it, "")
            elif token == "--mode":
                args["mode"] = next(it, "")
            elif token == "--name":
                args["agent_name"] = next(it, "")
            elif token == "--dest":
                args["dest"] = next(it, "")
            elif token == "--agent-dir":
                args["agent_dir"] = next(it, "")
            elif token == "--command":
                args["command"] = next(it, "")
            elif token == "--session-id":
                val = next(it, "")
                args["opencode_session_id"] = val
                args["session_id"] = val
            elif token == "--api-base-url":
                args["api_base_url"] = next(it, "")
            elif token == "--api-key":
                args["api_key"] = next(it, "")
            elif token.startswith("--"):
                raise ValueError(f"unknown flag: {token}")
        return args

    def _from_env(self) -> RuntimeConfig:
        return RuntimeConfig(
            provider=os.environ.get("AGENTX_PROVIDER", BUILTIN_PROVIDER),
            model=os.environ.get("AGENTX_MODEL", BUILTIN_MODEL),
            run_root=os.environ.get("AGENTX_RUN_ROOT", BUILTIN_RUN_ROOT),
            timeout_seconds=int(os.environ.get("AGENTX_TIMEOUT_SECONDS", str(BUILTIN_TIMEOUT))),
            opencode_base_url=os.environ.get("AGENTX_OPENCODE_BASE_URL", "http://127.0.0.1:14096"),
            opencode_api_key=os.environ.get("AGENTX_OPENCODE_API_KEY", ""),
            opencode_session_id=os.environ.get("AGENTX_OPENCODE_SESSION_ID", ""),
            api_base_url=os.environ.get("AGENTX_API_BASE_URL", "http://127.0.0.1:11434/v1"),
            api_key=os.environ.get("AGENTX_API_KEY", ""),
            session_id=os.environ.get("AGENTX_SESSION_ID", ""),
        )

    def _apply_args(self, config: RuntimeConfig, args: dict[str, Any]) -> None:
        for key, value in args.items():
            if hasattr(config, key):
                setattr(config, key, value)
        config.mock = config.mock or config.provider == "mock"
