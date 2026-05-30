"""L1 framework target tests — validates taxonomy, promotion rules, and evaluation criteria."""
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

    def test_taxonomy_has_framework_required_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        fw = tax.get("framework_target", {})
        caps = set(fw.get("required_capabilities", []))
        required = {
            "module_registry", "extension_contracts", "composition_rules",
            "evaluation_suite", "promotion_rules", "artifact_packaging",
            "rollback_migration", "compatibility_surface", "evidence_traceability",
        }
        missing = required - caps
        assert not missing, f"Missing required capabilities in taxonomy: {missing}"

    def test_taxonomy_has_forbidden_capabilities(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        fw = tax.get("framework_target", {})
        forbidden = set(fw.get("forbidden_capabilities", []))
        required = {
            "l0_runtime_self_modification", "governance_bypass",
            "evidence_free_promotion", "separate_required_framework_seed_repo",
        }
        missing = required - forbidden
        assert not missing, f"Missing forbidden capabilities in taxonomy: {missing}"

    def test_taxonomy_has_migration_rule(self):
        tax = _load_yaml("L1/target_taxonomy.yaml")
        assert tax is not None
        assert "migration" in tax
        assert tax["migration"].get("default_for_missing_target_kind") == "agent"


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
