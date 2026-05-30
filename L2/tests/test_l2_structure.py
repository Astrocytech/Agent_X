"""L2 structure tests — validates required directories and files exist."""
import os

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_DIRS = [
    "docs", "profiles", "blueprints", "evaluation_specs", "integration_specs",
    "extension_specs", "standards", "fic", "fic/units", "ecosystem",
    "ecosystem/ecosystem-schemas", "sib", "sib/sib-schemas", "eqc",
    "eqc/manifests", "eqc/procedures", "eqc/operators", "eqc/tests",
    "eqc/schemas", "generated", "evidence", "evidence/bootstrap",
    "validators", "tests",
]

REQUIRED_STANDARDS = [
    "AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_SIB_BRIDGE_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_ES_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_v0_4.md",
]

REQUIRED_PROFILES = [
    "coding_agent.yaml",
    "symbolic_regression_controller.yaml",
    "research_agent.yaml",
    "repo_maintenance_agent.yaml",
]


def test_required_dirs_exist():
    for rel in REQUIRED_DIRS:
        assert os.path.isdir(os.path.join(L2_DIR, rel)), f"Missing required directory: {rel}"


def test_standards_exist():
    for name in REQUIRED_STANDARDS:
        assert os.path.isfile(os.path.join(L2_DIR, "standards", name)), f"Missing standard: {name}"


def test_profiles_exist():
    for name in REQUIRED_PROFILES:
        assert os.path.isfile(os.path.join(L2_DIR, "profiles", name)), f"Missing profile: {name}"


def test_fic_index_exists():
    assert os.path.isfile(os.path.join(L2_DIR, "fic", "index.l2-fic.yaml")), "Missing FIC index"


def test_sib_l1_handoff_map_exists():
    assert os.path.isfile(os.path.join(L2_DIR, "sib", "sib-l1-handoff-map.yaml")), "Missing SIB handoff map"
