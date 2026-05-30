"""L2 profile contract tests — validates profiles meet the model requirements."""
import os
import yaml

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_FIELDS = [
    "profile_id", "name", "status", "specialization_type",
    "purpose", "allowed_inputs", "expected_outputs",
    "required_l1_units", "forbidden_actions", "risk_level",
]

FORBIDDEN_ACTIONS_CHECK = [
    "direct L0 modification",
    "direct L1 modification without FIC",
    "ungoverned tool execution",
]


def test_every_profile_has_required_fields():
    profiles_dir = os.path.join(L2_DIR, "profiles")
    for fname in os.listdir(profiles_dir):
        if not fname.endswith(".yaml"):
            continue
        fp = os.path.join(profiles_dir, fname)
        with open(fp) as fh:
            data = yaml.safe_load(fh)
        assert data is not None, f"{fname} is empty or invalid YAML"
        for field in REQUIRED_FIELDS:
            assert field in data, f"{fname} missing required field: {field}"


def test_every_profile_has_forbidden_actions():
    profiles_dir = os.path.join(L2_DIR, "profiles")
    for fname in os.listdir(profiles_dir):
        if not fname.endswith(".yaml"):
            continue
        fp = os.path.join(profiles_dir, fname)
        with open(fp) as fh:
            data = yaml.safe_load(fh)
        forbidden = data.get("forbidden_actions", [])
        for action in FORBIDDEN_ACTIONS_CHECK:
            assert any(action.lower() in fa.lower() for fa in forbidden), (
                f"{fname} missing forbidden action: {action}"
            )


def test_every_profile_has_implementation_blocked():
    profiles_dir = os.path.join(L2_DIR, "profiles")
    for fname in os.listdir(profiles_dir):
        if not fname.endswith(".yaml"):
            continue
        fp = os.path.join(profiles_dir, fname)
        with open(fp) as fh:
            data = yaml.safe_load(fh)
        impl = data.get("implementation_allowed", data.get("implementation_allowed_without_l1", True))
        assert impl is False, f"{fname} has implementation_allowed not false"
        runtime = data.get("direct_runtime_allowed", True)
        assert runtime is False, f"{fname} has direct_runtime_allowed not false"
