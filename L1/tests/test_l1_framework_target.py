"""L1 framework target tests — validates taxonomy, promotion rules, and evaluation criteria
using production validators from L1/validators/."""
import os
import yaml

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def _load_yaml(rel_path):
    full = os.path.join(REPO_ROOT, rel_path)
    if not os.path.isfile(full):
        return None
    with open(full) as f:
        return yaml.safe_load(f)


class TestTargetTaxonomy:
    def test_taxonomy_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml")
        assert os.path.isfile(path), "L1/target_taxonomy.yaml not found"

    def test_taxonomy_includes_framework(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        assert "framework" in tax.get("allowed_target_kinds", [])

    def test_taxonomy_includes_agent_controller_orchestrator(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        kinds = set(tax.get("allowed_target_kinds", []))
        for k in ["agent", "controller", "orchestrator"]:
            assert k in kinds, f"Missing target kind: {k}"

    def test_taxonomy_has_framework_section(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        assert "framework" in tax, "Missing framework section"

    def test_taxonomy_framework_has_required_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        caps = tax.get("framework", {}).get("required_capabilities", [])
        assert len(caps) > 0, "framework.required_capabilities is empty"

    def test_taxonomy_framework_has_forbidden_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        forbidden = tax.get("framework", {}).get("forbidden_capabilities", [])
        assert len(forbidden) > 0, "framework.forbidden_capabilities is empty"

    def test_taxonomy_has_migration_rule(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        mig = tax.get("migration", {})
        assert mig.get("missing_target_kind_default") == "agent"
        assert mig.get("allow_legacy_profiles_without_target_kind") is True


class TestTaxonomyValidator:
    def test_taxonomy_validator_production(self):
        """Test that the production taxonomy validator passes."""
        from L1.validators.validate_target_taxonomy import validate
        result = validate()
        assert result.status in ("PASS", "WARNING"), f"Validator returned {result.status}: {result.errors}"


class TestFrameworkEvaluationCriteria:
    def test_evaluation_criteria_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "evaluators", "framework_evaluation_criteria.md")
        assert os.path.isfile(path)

    def test_evaluation_criteria_has_required_content(self):
        path = os.path.join(REPO_ROOT, "L1", "evaluators", "framework_evaluation_criteria.md")
        with open(path) as f:
            content = f.read()
        assert "generality" in content.lower()
        assert "modularity" in content.lower()
        assert "governability" in content.lower()
        assert "evaluability" in content.lower()
        assert "replayability" in content.lower()
        assert "extensibility" in content.lower()
        assert "minimality" in content.lower()
        assert "7/10" in content


class TestFrameworkPromotionRules:
    def test_promotion_rules_exist(self):
        path = os.path.join(REPO_ROOT, "L1", "promotion", "framework_promotion_rules.md")
        assert os.path.isfile(path)

    def test_promotion_rules_include_statuses(self):
        path = os.path.join(REPO_ROOT, "L1", "promotion", "framework_promotion_rules.md")
        with open(path) as f:
            content = f.read()
        for status in ["rejected", "revise", "experimental_framework_profile", "exportable_framework_package"]:
            assert status in content


class TestFrameworkPackageManifestSchema:
    def test_schema_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "schemas", "framework_package_manifest.schema.yaml")
        assert os.path.isfile(path)

    def test_schema_has_required_fields(self):
        schema = _load_yaml("L1/schemas/framework_package_manifest.schema.yaml")
        assert schema is not None
        fields = set(schema.get("fields", {}).keys())
        for req in ["id", "name", "version", "target_kind", "contracts", "promotion", "validation"]:
            assert req in fields, f"Missing required schema field: {req}"


class TestFrameworkTemplates:
    def test_comparison_template_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "templates", "framework_candidate_comparison.md")
        assert os.path.isfile(path)

    def test_evidence_record_template_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "templates", "framework_evolution_evidence_record.md")
        assert os.path.isfile(path)


class TestFrameworkManifestValidator:
    def test_valid_manifest_passes_production_validator(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "L1" / "fixtures" / "framework_manifest_valid.yaml"
        errors = validate_manifest(path)
        assert not errors, f"Valid manifest should pass: {errors}"

    def test_invalid_missing_contracts_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "L1" / "fixtures" / "framework_manifest_invalid_missing_contracts.yaml"
        errors = validate_manifest(path)
        assert any("contract" in e.lower() for e in errors), f"Expected contract errors, got: {errors}"

    def test_invalid_missing_promotion_status_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "L1" / "fixtures" / "framework_manifest_invalid_missing_promotion_status.yaml"
        errors = validate_manifest(path)
        assert any("promotion.status" in e for e in errors), f"Expected promotion.status error, got: {errors}"

    def test_invalid_bad_promotion_status_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "L1" / "fixtures" / "framework_manifest_invalid_bad_promotion_status.yaml"
        errors = validate_manifest(path)
        assert any("Invalid promotion status" in e for e in errors), f"Expected bad status error, got: {errors}"

    def test_invalid_missing_compatibility_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        from pathlib import Path
        path = Path(__file__).resolve().parent.parent.parent / "L1" / "fixtures" / "framework_manifest_invalid_missing_compatibility.yaml"
        errors = validate_manifest(path)
        assert any("compatibility" in e.lower() for e in errors), f"Expected compatibility errors, got: {errors}"


class TestFrameworkFixturesStructure:
    def test_fixtures_directory_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "fixtures")
        assert os.path.isdir(path)

    def test_expected_fixtures_exist(self):
        expected = [
            "framework_manifest_valid.yaml",
            "framework_manifest_invalid_missing_contracts.yaml",
            "framework_candidate_invalid_governance_bypass.yaml",
            "framework_candidate_invalid_l0_self_modification.yaml",
            "framework_candidate_invalid_hidden_state.yaml",
            "framework_candidate_invalid_separate_seed_repo.yaml",
        ]
        for fname in expected:
            path = os.path.join(REPO_ROOT, "L1", "fixtures", fname)
            assert os.path.isfile(path), f"Missing fixture: {fname}"

    def test_backward_compat_fixtures_exist(self):
        expected = [
            "agent_target_valid_minimal.yaml",
            "controller_target_valid_minimal.yaml",
            "orchestrator_target_valid_minimal.yaml",
        ]
        for fname in expected:
            path = os.path.join(REPO_ROOT, "L1", "fixtures", fname)
            assert os.path.isfile(path), f"Missing backward compat fixture: {fname}"
