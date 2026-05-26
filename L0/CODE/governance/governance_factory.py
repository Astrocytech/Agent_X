"""Deprecated — governance factory is not required by L0 runtime. See local_governance_port.py."""


from pathlib import Path
from typing import Any

BUILTIN_PROFILES_DIR = Path(__file__).resolve().parent.parent / "profiles" / "builtin"
BUILTIN_PROFILE_IDS = ["generalist"]

logger = __import__("logging").getLogger(__name__)


class _SeedGovernanceBus:
    """Minimal governance bus that denies by default when no engines are loaded."""

    def __init__(self, governance_mode: str = "strict_passthrough", **engines):
        self.governance_mode = governance_mode
        self._engines = engines

    def decide(self, request):
        from core_kernel.contracts.governance_contracts import GovernanceDecision

        return GovernanceDecision(
            allowed=False,
            reason="denied:no_governance_engines",
        )


def build_governance_bus(mode: str = "strict_passthrough") -> object:

    permission_engine = _try_import_engine("governance.permission_engine", "PermissionEngine")
    risk_engine = _try_import_engine("governance.risk_engine", "RiskMatrix")
    secret_engine = _try_import_engine("governance.secret_engine", "SecretEngine")
    sandbox_engine = _try_import_engine("governance.sandbox_engine", "SandboxEngine")
    self_mod_engine = _try_import_engine("governance.self_mod_engine", "SelfModEngine")
    irreversible_engine = _try_import_engine(
        "governance.irreversible_engine", "IrreversibleActionEngine"
    )
    policy_engine = _try_import_engine("governance.policy_engine", "PolicyEngine")

    # Register default permission rules so actions are not universally denied
    if permission_engine is not None:
        _register_default_permissions(permission_engine)

    # memory_governance is a module of free functions, not a class
    memory_governance = _try_import_module("governance.memory_governance_engine")

    return _SeedGovernanceBus(
        permission_engine=permission_engine,
        risk_engine=risk_engine,
        secret_engine=secret_engine,
        sandbox_policy=sandbox_engine,
        self_mod_policy=self_mod_engine,
        irreversible_policy=irreversible_engine,
        memory_governance=memory_governance,
        policy_engine=policy_engine,
        governance_mode=mode,
    )


def _register_default_permissions(engine: Any) -> None:
    """Register default permission rules so common actions are allowed.

    Without these, PermissionEngine returns ``granted=False`` for every
    action because no rules exist.  Profiles can override via their own
    allowed_tools / forbidden_tools configuration.
    """
    import logging

    log = logging.getLogger(__name__)
    actions = [
        "echo",
        "memory_write",
        "memory_read",
        "tool_call",
        "checkpoint",
        "rollback",
        "plan",
        "execute",
        "observe",
        "evaluate",
        "emit_answer",
        "list_tools",
        "memory.read",
        "memory.write",
        "trace.read",
        "artifact.read",
        "artifact.write",
        "eval.run",
        "profile.inspect",
    ]
    for action in actions:
        try:
            engine.add_rule(action, allowed_profiles=["*"])
        except Exception as exc:
            log.debug("Could not register default permission for %s: %s", action, exc)


def load_builtin_profiles(
    profile_repository: Any,
    profiles_dir: str | Path = BUILTIN_PROFILES_DIR,
    profile_ids: list[str] | None = None,
) -> int:
    """Load builtin YAML profiles into a ``ProfileRepository``.

    Returns the number of profiles loaded.
    """

    loader = _ProfileYAMLLoader(Path(profiles_dir))
    loaded = 0
    for pid in profile_ids or BUILTIN_PROFILE_IDS:
        try:
            data = loader.load_yaml(pid)
            profile_repository.register_profile(pid, data)
            loaded += 1
        except Exception as exc:
            logger.warning("Failed to load builtin profile %s: %s", pid, exc)
    return loaded


def _try_import_engine(module_path: str, class_name: str):
    """Lazy-import an engine class, returning ``None`` on failure."""
    try:
        mod = __import__(module_path, fromlist=[class_name])
        cls = getattr(mod, class_name)
        return cls()
    except Exception as exc:
        logger.debug("Governance engine %s.%s unavailable: %s", module_path, class_name, exc)
        return None


def _try_import_module(module_path: str):
    """Lazy-import a module, returning ``None`` on failure."""
    try:
        return __import__(module_path, fromlist=[""])
    except Exception as exc:
        logger.debug("Governance module %s unavailable: %s", module_path, exc)
        return None


class _ProfileYAMLLoader:
    """Minimal YAML loader for builtin profile definitions."""

    def __init__(self, profiles_dir: Path) -> None:
        self._profiles_dir = profiles_dir

    def load_yaml(self, profile_id: str) -> dict:
        path = self._profiles_dir / f"{profile_id}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Profile YAML not found: {path}")
        import yaml

        return yaml.safe_load(path.read_text())
