"""L2 framework target tests — validates framework_seed profile, fixtures, and backward compat."""
import os
import yaml

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(L2_DIR)


def _load_yaml(rel_path):
    full = os.path.join(REPO_ROOT, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full) as f:
        return yaml.safe_load(f)


ALLOWED_TARGET_KINDS = {
    "agent", "controller", "orchestrator", "framework",
    "toolchain", "runtime", "ui", "evaluator",
}

COMMON_REQUIRED_FIELDS = {
    "id", "name", "version", "target_kind", "purpose", "constraints", "evaluation",
}

FRAMEWORK_REQUIRED_FIELDS = {
    "non_goals", "required_capabilities", "required_interfaces",
    "promotion", "packaging", "rollback", "compatibility",
}

FRAMEWORK_REQUIRED_CAPABILITIES = {
    "module_registry", "extension_contracts", "composition_rules",
    "evaluation_suite", "promotion_rules", "artifact_packaging",
    "rollback_migration", "compatibility_surface", "evidence_traceability",
}

FRAMEWORK_FORBIDDEN_FLAGS = {
    "l0_runtime_self_modification", "governance_bypass",
    "evidence_free_promotion", "hidden_state_without_replay",
    "provider_locked_core", "irreversible_export_without_approval",
    "separate_required_framework_seed_repo",
}


def _has_field(profile, field_name):
    if field_name in profile:
        return True
    aliases = {"id": ["profile_id", "global_profile_id"], "evaluation": ["evaluation_refs"]}
    if field_name in aliases:
        for alias in aliases[field_name]:
            if alias in profile:
                return True
    return False


def validate_target_profile(profile):
    errors = []

    missing_common = [f for f in COMMON_REQUIRED_FIELDS if not _has_field(profile, f)]
    for field in sorted(missing_common):
        errors.append(f"missing common field: {field}")

    target_kind = profile.get("target_kind")
    if target_kind not in ALLOWED_TARGET_KINDS:
        errors.append(f"invalid target_kind: {target_kind}")
        return errors

    if target_kind == "framework":
        missing_framework = FRAMEWORK_REQUIRED_FIELDS - set(profile.keys())
        for field in sorted(missing_framework):
            errors.append(f"missing framework field: {field}")

        declared_capabilities = set(profile.get("required_capabilities", []))
        missing_capabilities = FRAMEWORK_REQUIRED_CAPABILITIES - declared_capabilities
        for capability in sorted(missing_capabilities):
            errors.append(f"missing framework capability: {capability}")

        forbidden = set(profile.get("forbidden_capabilities", [])) | set(profile.get("must_not", []))
        declared = set(profile.get("required_capabilities", [])) | set(profile.get("features", []))
        for flag in sorted(FRAMEWORK_FORBIDDEN_FLAGS & declared):
            errors.append(f"forbidden framework capability required: {flag}")

        if profile.get("requires_l0_runtime_self_modification") is True:
            errors.append("framework target must not require L0 runtime self-modification")

        if profile.get("requires_separate_framework_seed_repo") is True:
            errors.append("framework target must not require a separate root Framework_X seed repo")

    return errors


class TestFrameworkProfileValid:
    def test_framework_seed_profile_exists(self):
        path = os.path.join(L2_DIR, "profiles", "framework_seed.yaml")
        assert os.path.isfile(path), "framework_seed.yaml profile not found"

    def test_framework_seed_profile_validates(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert errors == [], f"Validation errors: {errors}"

    def test_framework_seed_profile_target_kind(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        assert profile.get("target_kind") == "framework"

    def test_framework_seed_has_all_required_capabilities(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        caps = set(profile.get("required_capabilities", []))
        missing = FRAMEWORK_REQUIRED_CAPABILITIES - caps
        assert not missing, f"Missing required capabilities: {missing}"

    def test_framework_seed_no_forbidden_capabilities(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        forbidden = set(profile.get("forbidden_capabilities", []))
        allowed = FRAMEWORK_FORBIDDEN_FLAGS & forbidden
        assert allowed == FRAMEWORK_FORBIDDEN_FLAGS, (
            f"Missing forbidden flags: {FRAMEWORK_FORBIDDEN_FLAGS - allowed}"
        )


class TestFrameworkProfileInvalid:
    def test_invalid_target_kind_rejected(self):
        errors = validate_target_profile({
            "id": "test", "name": "test", "version": "1",
            "target_kind": "unicorn", "purpose": "x", "constraints": {}, "evaluation": {},
        })
        assert any("invalid target_kind" in e for e in errors)

    def test_missing_common_fields_rejected(self):
        errors = validate_target_profile({"target_kind": "agent"})
        assert any("missing common field" in e for e in errors)

    def test_missing_framework_fields_rejected(self):
        errors = validate_target_profile({
            "id": "test", "name": "test", "version": "1",
            "target_kind": "framework", "purpose": "x", "constraints": {}, "evaluation": {},
        })
        assert any("missing framework field" in e for e in errors)

    def test_missing_framework_capabilities_rejected(self):
        errors = validate_target_profile({
            "id": "test", "name": "test", "version": "1",
            "target_kind": "framework", "purpose": "x", "constraints": {}, "evaluation": {},
            "non_goals": [], "required_capabilities": [], "required_interfaces": {},
            "promotion": {}, "packaging": {}, "rollback": {}, "compatibility": {},
        })
        assert any("missing framework capability" in e for e in errors)


class TestExistingTargetBackwardCompat:
    def test_existing_agent_target_valid_minimal(self):
        profile = _load_yaml("L1/fixtures/agent_target_valid_minimal.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert errors == [], f"Agent target should validate: {errors}"

    def test_existing_controller_target_valid_minimal(self):
        profile = _load_yaml("L1/fixtures/controller_target_valid_minimal.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert errors == [], f"Controller target should validate: {errors}"

    def test_existing_orchestrator_target_valid_minimal(self):
        profile = _load_yaml("L1/fixtures/orchestrator_target_valid_minimal.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert errors == [], f"Orchestrator target should validate: {errors}"

    def test_existing_l2_profiles_still_valid_without_target_kind(self):
        for fname in os.listdir(os.path.join(L2_DIR, "profiles")):
            if not fname.endswith(".yaml"):
                continue
            path = os.path.join(L2_DIR, "profiles", fname)
            with open(path) as fh:
                content = fh.read()
            if "target_kind:" not in content:
                continue
            profile = yaml.safe_load(content)
            if profile.get("target_kind") == "framework":
                continue
            errors = validate_target_profile(profile)
            if errors:
                assert fname == "framework_seed.yaml", f"Unexpected error in {fname}: {errors}"


class TestFrameworkManifestFixtures:
    def test_valid_manifest_loads(self):
        manifest = _load_yaml("L1/fixtures/framework_manifest_valid.yaml")
        assert manifest is not None
        assert manifest.get("target_kind") == "framework"
        assert manifest.get("promotion", {}).get("status") == "experimental_framework_profile"

    def test_invalid_missing_contracts_detected(self):
        manifest = _load_yaml("L1/fixtures/framework_manifest_invalid_missing_contracts.yaml")
        assert manifest is not None
        contracts = manifest.get("contracts", {})
        missing = [k for k in ["extension_contract", "promotion_contract", "rollback_contract"] if k not in contracts]
        assert missing, "Fixture should be missing extension_contract, promotion_contract, rollback_contract"

    def test_governance_bypass_fixture_rejected(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_governance_bypass.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert any("forbidden" in e and "governance_bypass" in e for e in errors), (
            f"Expected governance_bypass rejection, got: {errors}"
        )

    def test_l0_self_modification_fixture_rejected(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_l0_self_modification.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert any("must not require L0 runtime self-modification" in e for e in errors), (
            f"Expected L0 self-modification rejection, got: {errors}"
        )

    def test_separate_seed_repo_fixture_rejected(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_separate_seed_repo.yaml")
        assert profile is not None
        errors = validate_target_profile(profile)
        assert any("must not require a separate root Framework_X seed repo" in e for e in errors), (
            f"Expected separate seed repo rejection, got: {errors}"
        )

    def test_hidden_state_fixture_detected(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_hidden_state.yaml")
        assert profile is not None
        assert profile.get("hidden_state_without_replay") is True
