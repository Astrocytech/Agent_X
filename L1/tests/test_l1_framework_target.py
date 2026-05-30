"""L1 framework target tests — validates taxonomy, promotion rules, and evaluation criteria
using production validators from L1/validators/."""

import os
from pathlib import Path

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

    def test_taxonomy_has_target_kinds_framework(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        assert "framework" in tax.get("target_kinds", {})

    def test_taxonomy_has_framework_rules_section(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        assert "framework_rules" in tax, "Missing framework_rules section"

    def test_taxonomy_framework_rules_has_required_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        caps = tax.get("framework_rules", {}).get("required_capabilities", [])
        assert len(caps) > 0, "framework_rules.required_capabilities is empty"

    def test_taxonomy_framework_rules_has_forbidden_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        forbidden = tax.get("framework_rules", {}).get("forbidden_capabilities", [])
        assert len(forbidden) > 0, "framework_rules.forbidden_capabilities is empty"

    def test_taxonomy_has_migration_rule(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        mig = tax.get("migration", {})
        assert mig.get("missing_target_kind_default") == "agent"
        assert mig.get("allow_legacy_profiles_without_target_kind") is True


class TestTaxonomyValidator:
    def test_taxonomy_validator_production(self):
        from L1.validators.validate_target_taxonomy import validate
        result = validate()
        assert result.status in ("PASS", "WARNING"), (
            f"Validator returned {result.status}: {result.errors}"
        )

    def test_taxonomy_fails_without_framework_rules(self):
        from L1.validators.validate_target_taxonomy import validate
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("allowed_target_kinds: [agent, framework]\n")
            f.write("target_kinds:\n  framework:\n    description: test\n")
            f.write("migration:\n  missing_target_kind_default: agent\n")
            f.write("  allow_legacy_profiles_without_target_kind: true\n")
            tmp = f.name
        try:
            result = validate(tmp)
            assert result.status == "FAIL", (
                f"Expected FAIL without framework_rules, got {result.status}"
            )
            assert any("framework_rules" in e for e in result.errors), (
                f"Expected framework_rules error, got: {result.errors}"
            )
        finally:
            os.unlink(tmp)

    def test_taxonomy_fails_without_target_kinds_framework(self):
        from L1.validators.validate_target_taxonomy import validate
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("allowed_target_kinds: [agent, framework]\n")
            f.write("target_kinds:\n  agent:\n    description: test\n")
            f.write("framework_rules:\n  required_capabilities: [a]\n")
            f.write("  forbidden_capabilities: [b]\n")
            f.write("  required_manifest_fields: [c]\n")
            f.write("migration:\n  missing_target_kind_default: agent\n")
            f.write("  allow_legacy_profiles_without_target_kind: true\n")
            tmp = f.name
        try:
            result = validate(tmp)
            assert result.status == "FAIL", (
                f"Expected FAIL without target_kinds.framework, got {result.status}"
            )
            assert any("target_kinds.framework" in e for e in result.errors), (
                f"Expected target_kinds.framework error, got: {result.errors}"
            )
        finally:
            os.unlink(tmp)

    def test_taxonomy_fails_without_framework_in_allowed(self):
        from L1.validators.validate_target_taxonomy import validate
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("allowed_target_kinds: [agent]\n")
            f.write("target_kinds:\n  framework:\n    description: test\n")
            f.write("  agent:\n    description: test\n")
            f.write("framework_rules:\n  required_capabilities: [a]\n")
            f.write("  forbidden_capabilities: [b]\n")
            f.write("  required_manifest_fields: [c]\n")
            f.write("migration:\n  missing_target_kind_default: agent\n")
            f.write("  allow_legacy_profiles_without_target_kind: true\n")
            tmp = f.name
        try:
            result = validate(tmp)
            assert result.status == "FAIL", (
                f"Expected FAIL without framework in allowed, got {result.status}"
            )
            assert any("must include 'framework'" in e for e in result.errors), (
                f"Expected framework in allowed error, got: {result.errors}"
            )
        finally:
            os.unlink(tmp)


class TestFrameworkEvaluationCriteria:
    def test_evaluation_criteria_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "evaluators", "framework_evaluation_criteria.md")
        assert os.path.isfile(path)

    def test_evaluation_criteria_has_required_content(self):
        path = os.path.join(REPO_ROOT, "L1", "evaluators", "framework_evaluation_criteria.md")
        with open(path) as f:
            content = f.read()
        for term in ["generality", "modularity", "governability", "evaluability",
                      "replayability", "extensibility", "minimality", "7/10"]:
            assert term in content.lower() or term in content


class TestFrameworkPromotionRules:
    def test_promotion_rules_exist(self):
        path = os.path.join(REPO_ROOT, "L1", "promotion", "framework_promotion_rules.md")
        assert os.path.isfile(path)

    def test_promotion_rules_include_statuses(self):
        path = os.path.join(REPO_ROOT, "L1", "promotion", "framework_promotion_rules.md")
        with open(path) as f:
            content = f.read()
        for status in ["rejected", "revise", "experimental_framework_profile",
                        "exportable_framework_package"]:
            assert status in content


class TestFrameworkPackageManifestSchema:
    def test_schema_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "schemas", "framework_package_manifest.schema.yaml")
        assert os.path.isfile(path)

    def test_schema_has_required_fields(self):
        schema = _load_yaml("L1/schemas/framework_package_manifest.schema.yaml")
        assert schema is not None
        fields = set(schema.get("fields", {}).keys())
        for req in ["id", "name", "version", "target_kind", "contracts",
                     "promotion", "validation"]:
            assert req in fields, f"Missing required schema field: {req}"


class TestFrameworkTemplates:
    def test_comparison_template_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "templates",
                            "framework_candidate_comparison.md")
        assert os.path.isfile(path)

    def test_evidence_record_template_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "templates",
                            "framework_evolution_evidence_record.md")
        assert os.path.isfile(path)


class TestFrameworkManifestValidator:
    def test_valid_manifest_passes_production_validator(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "framework_manifests" / "framework_seed_manifest.example.yaml"
        errors = validate_manifest(path)
        assert not errors, f"Valid manifest should pass: {errors}"

    def test_valid_manifest_fixture_passes(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_valid.yaml"
        errors = validate_manifest(path)
        assert not errors, f"Valid manifest fixture should pass: {errors}"

    def test_invalid_missing_contracts_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_invalid_missing_contracts.yaml"
        errors = validate_manifest(path)
        assert len(errors) > 0, "Expected errors for missing contracts manifest"

    def test_invalid_missing_promotion_status_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_invalid_missing_promotion_status.yaml"
        errors = validate_manifest(path)
        assert any("promotion" in e or "manifest_version" in e for e in errors), (
            f"Expected promotion/manifest_version errors, got: {errors}"
        )

    def test_invalid_bad_promotion_status_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_invalid_bad_promotion_status.yaml"
        errors = validate_manifest(path)
        assert any("promotion" in e or "manifest_version" in e for e in errors), (
            f"Expected promotion/manifest_version errors, got: {errors}"
        )

    def test_invalid_missing_compatibility_fails(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_invalid_missing_compatibility.yaml"
        errors = validate_manifest(path)
        assert len(errors) > 0, "Expected errors for missing compatibility manifest"

    def test_manifest_rejects_l0_self_modification(self):
        from L1.validators.validate_framework_manifest import validate_manifest
        path = Path(__file__).resolve().parent.parent.parent / "L1" \
            / "fixtures" / "framework_manifest_invalid_missing_rollback.yaml"
        errors = validate_manifest(path)
        assert len(errors) > 0, "Expected errors for invalid manifest"

    def test_validate_all_includes_target_taxonomy(self):
        from L1.validators.validate_all import run_all
        results = run_all()
        names = [r["name"] for r in results]
        assert "TargetTaxonomy" in names, (
            f"Expected TargetTaxonomy in validate_all, got: {names}"
        )

    def test_validate_all_includes_framework_manifests(self):
        from L1.validators.validate_all import run_all
        results = run_all()
        names = [r["name"] for r in results]
        assert "FrameworkManifests" in names, (
            f"Expected FrameworkManifests in validate_all, got: {names}"
        )


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

    def test_example_manifest_exists(self):
        path = os.path.join(REPO_ROOT, "L1", "framework_manifests",
                            "framework_seed_manifest.example.yaml")
        assert os.path.isfile(path), "Example manifest not found"
