"""L2 framework target tests — validates framework_seed profile, fixtures, and backward compat
using production validators from L2/validators/."""

import os
import tempfile

import yaml

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(L2_DIR)


def _load_yaml(rel_path):
    full = os.path.join(REPO_ROOT, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full) as f:
        return yaml.safe_load(f)


def _profiles_dir():
    return os.path.join(L2_DIR, "profiles")


def _taxonomy_path():
    return os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml")


class TestFrameworkProfileValid:
    def test_framework_seed_profile_exists(self):
        path = os.path.join(L2_DIR, "profiles", "framework_seed.yaml")
        assert os.path.isfile(path), "framework_seed.yaml profile not found"

    def test_framework_seed_profile_validates_with_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=_profiles_dir(),
            taxonomy_path=_taxonomy_path(),
        )
        framework_errors = [e for e in errors if "framework_seed.yaml" in e]
        assert not framework_errors, (
            f"Production validator errors for framework_seed.yaml: {framework_errors}"
        )

    def test_framework_seed_profile_target_kind(self):
        profile = _load_yaml("L2/profiles/framework_seed.yaml")
        assert profile is not None
        assert profile.get("target_kind") == "framework"


class TestFrameworkProfileInvalid:
    def test_invalid_target_kind_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        with tempfile.TemporaryDirectory() as td:
            bad_profile = os.path.join(td, "bad.yaml")
            with open(bad_profile, "w") as f:
                f.write("target_kind: unicorn\nname: bad\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=_taxonomy_path(),
            )
            assert any("Unknown target_kind" in e for e in errors), (
                f"Expected unknown target_kind rejection, got: {errors}"
            )

    def test_new_profile_without_target_kind_fails(self):
        from L2.validators.validate_target_profiles import validate_profiles
        with tempfile.TemporaryDirectory() as td:
            new_profile = os.path.join(td, "new_profile.yaml")
            with open(new_profile, "w") as f:
                f.write("name: new profile without target_kind\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=_taxonomy_path(),
            )
            assert any("must declare target_kind" in e for e in errors), (
                f"Expected target_kind requirement, got: {errors}"
            )

    def test_legacy_profiles_without_target_kind_pass(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=_profiles_dir(),
            taxonomy_path=_taxonomy_path(),
        )
        legacy_names = [
            "coding_agent.yaml", "symbolic_regression_controller.yaml",
            "research_agent.yaml", "repo_maintenance_agent.yaml",
            "orchestrator.yaml",
        ]
        for lname in legacy_names:
            legacy_errors = [e for e in errors if lname in e]
            assert not legacy_errors, (
                f"Legacy profile {lname} should pass, got: {legacy_errors}"
            )

    def test_governance_bypass_fixture_rejected_by_production_validator(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=_taxonomy_path(),
        )
        gov_errors = [e for e in errors if "governance_bypass" in e]
        assert gov_errors, f"Expected governance_bypass rejection, got: {errors}"

    def test_l0_self_modification_fixture_rejected(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=_taxonomy_path(),
        )
        l0_errors = [e for e in errors if "l0_self_modification" in e or "L0" in e]
        assert l0_errors, f"Expected L0 self-modification rejection, got: {errors}"

    def test_separate_seed_repo_fixture_rejected(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=_taxonomy_path(),
        )
        repo_errors = [e for e in errors if "separate" in e and "seed" in e]
        assert repo_errors, f"Expected separate seed repo rejection, got: {errors}"

    def test_hidden_state_fixture_rejected(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=os.path.join(REPO_ROOT, "L1", "fixtures"),
            taxonomy_path=_taxonomy_path(),
        )
        hidden_errors = [e for e in errors if "hidden" in e and "replay" in e]
        assert hidden_errors, f"Expected hidden state rejection, got: {errors}"

    def test_forbidden_capability_in_required_capabilities_fails(self):
        from L2.validators.validate_target_profiles import validate_profiles
        with tempfile.TemporaryDirectory() as td:
            bad_profile = os.path.join(td, "bad_fw.yaml")
            with open(bad_profile, "w") as f:
                f.write("target_kind: framework\n")
                f.write("required_capabilities:\n")
                f.write("  - plugin_registry\n")
                f.write("  - l0_runtime_self_modification\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=_taxonomy_path(),
            )
            assert any("l0_runtime_self_modification" in e for e in errors), (
                f"Expected forbidden capability rejection, got: {errors}"
            )

    def test_forbidden_capability_in_features_fails(self):
        from L2.validators.validate_target_profiles import validate_profiles
        with tempfile.TemporaryDirectory() as td:
            bad_profile = os.path.join(td, "bad_fw_features.yaml")
            with open(bad_profile, "w") as f:
                f.write("target_kind: framework\n")
                f.write("required_capabilities:\n")
                f.write("  - plugin_registry\n")
                f.write("features:\n")
                f.write("  - unmediated_tool_execution\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=_taxonomy_path(),
            )
            assert any("unmediated_tool_execution" in e for e in errors), (
                f"Expected forbidden feature rejection, got: {errors}"
            )

    def test_forbidden_capability_in_forbidden_actions_fails(self):
        from L2.validators.validate_target_profiles import validate_profiles
        with tempfile.TemporaryDirectory() as td:
            bad_profile = os.path.join(td, "bad_fw_actions.yaml")
            with open(bad_profile, "w") as f:
                f.write("target_kind: framework\n")
                f.write("required_capabilities:\n")
                f.write("  - plugin_registry\n")
                f.write("  - extension_boundary\n")
                f.write("  - evaluation_surface\n")
                f.write("  - governance_hooks\n")
                f.write("  - promotion_rules\n")
                f.write("  - packaging_export\n")
                f.write("  - rollback_plan\n")
                f.write("forbidden_actions:\n")
                f.write("  - l0_runtime_self_modification\n")
            errors = validate_profiles(
                profile_dir=td,
                taxonomy_path=_taxonomy_path(),
            )
            assert any("l0_runtime_self_modification" in e for e in errors), (
                f"Expected forbidden action rejection, got: {errors}"
            )


class TestNonFrameworkProfiles:
    def test_existing_non_framework_profiles_still_pass(self):
        from L2.validators.validate_target_profiles import validate_profiles
        errors = validate_profiles(
            profile_dir=_profiles_dir(),
            taxonomy_path=_taxonomy_path(),
        )
        non_fw_names = [
            "coding_agent.yaml", "symbolic_regression_controller.yaml",
            "research_agent.yaml", "repo_maintenance_agent.yaml",
            "orchestrator.yaml",
        ]
        for fname in non_fw_names:
            fname_errors = [e for e in errors if fname in e]
            assert not fname_errors, (
                f"Unexpected error in {fname}: {fname_errors}"
            )
