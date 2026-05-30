"""L2 framework target tests — validates framework_seed profile, fixtures, and backward compat
using production validators from L2/validators/."""
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


class TestFrameworkProfileValid:
    def test_framework_seed_profile_exists(self):
        path = os.path.join(L2_DIR, "profiles", "framework_seed.yaml")
        assert os.path.isfile(path), "framework_seed.yaml profile not found"

    def test_framework_seed_profile_validates_with_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(L2_DIR, "profiles"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        framework_errors = [e for e in errors if "framework_seed.yaml" in e]
        assert not framework_errors, f"Production validator errors for framework_seed.yaml: {framework_errors}"

    def test_framework_seed_profile_target_kind(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        assert profile.get("target_kind") == "framework"


class TestFrameworkProfileInvalid:
    def test_invalid_target_kind_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        import tempfile
        import os.path
        with tempfile.TemporaryDirectory() as td:
            bad_profile = os.path.join(td, "bad.yaml")
            with open(bad_profile, "w") as f:
                f.write("target_kind: unicorn\nname: bad\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
            )
            assert any("Unknown target_kind" in e or "unicorn" in e for e in errors), (
                f"Expected unknown target_kind rejection, got: {errors}"
            )

    def test_governance_bypass_fixture_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        gov_errors = [e for e in errors if "governance_bypass" in e]
        assert gov_errors, f"Expected governance_bypass rejection, got: {errors}"

    def test_l0_self_modification_fixture_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        l0_errors = [e for e in errors if "L0 runtime self-modification" in e]
        assert l0_errors, f"Expected L0 self-modification rejection, got: {errors}"

    def test_separate_seed_repo_fixture_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        repo_errors = [e for e in errors if "separate" in e and "seed" in e]
        assert repo_errors, f"Expected separate seed repo rejection, got: {errors}"

    def test_hidden_state_fixture_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        hidden_errors = [e for e in errors if "hidden" in e and "replay" in e]
        assert hidden_errors, f"Expected hidden state rejection, got: {errors}"


class TestExistingTargetBackwardCompat:
    def test_existing_l2_profiles_still_valid_without_target_kind(self):
        """Existing profiles without target_kind should be permitted via migration rule."""
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
            from L2.validators.validate_target_profiles import validate_profiles
            errors = validate_profiles(
                profile_dir=os.path.join(L2_DIR, "profiles"),
                taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
            )
            fname_errors = [e for e in errors if fname in e]
            assert not fname_errors, f"Unexpected error in {fname}: {fname_errors}"


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

    def test_governance_bypass_fixture_has_flag(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_governance_bypass.yaml")
        assert profile is not None
        caps = profile.get("required_capabilities", [])
        assert "ungoverned_tool_execution" in caps

    def test_l0_self_modification_fixture_has_flag(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_l0_self_modification.yaml")
        assert profile is not None
        assert profile.get("requires_l0_runtime_self_modification") is True

    def test_separate_seed_repo_fixture_has_flag(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_separate_seed_repo.yaml")
        assert profile is not None
        caps = profile.get("required_capabilities", [])
        assert "required_separate_framework_seed_repo" in caps

    def test_hidden_state_fixture_has_flag(self):
        profile = _load_yaml("L1/fixtures/framework_candidate_invalid_hidden_state.yaml")
        assert profile is not None
        caps = profile.get("required_capabilities", [])
        assert "hidden_non_replayable_state" in caps
