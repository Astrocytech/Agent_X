"""L1 structure tests — validates current standards-driven scaffold."""

import os

L1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

REQUIRED_L1_DIRS = [
    "controller",
    "docs",
    "fic",
    "standards",
    "sib",
    "ecosystem",
    "eqc",
    "generated",
    "evidence",
    "tests",
]

def test_required_l1_directories_exist():
    for rel in REQUIRED_L1_DIRS:
        assert os.path.isdir(os.path.join(L1_DIR, rel)), f"Missing required L1 directory: {rel}"

REQUIRED_STANDARDS = [
    "AGENT_X_L1_EQC_FIC_v0_6.md",
    "AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md",
]

def test_required_l1_standards_exist():
    for name in REQUIRED_STANDARDS:
        assert os.path.isfile(os.path.join(L1_DIR, "standards", name)), f"Missing standard: {name}"

ROOT_DUPLICATE_STANDARDS = [
    "AGENT_X_L1_EQC_FIC_v0_6.md",
    "AGENT_X_L1_PSEUDOCODE_TO_FIC_WORKFLOW_v0_6.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_SIB_v0_5.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_ES_v0_5.md",
    "AGENT_X_L1_LIGHTWEIGHT_EQC_v0_5.md",
]

REQUIRED_VALIDATORS = [
    "bootstrap_validate_mode_a.py",
    "common.py",
    "validate_all.py",
    "validate_eqc.py",
    "validate_es.py",
    "validate_fic.py",
    "validate_lockfile.py",
    "validate_sib.py",
]

def test_required_validator_files_exist():
    for name in REQUIRED_VALIDATORS:
        assert os.path.isfile(os.path.join(L1_DIR, "validators", name)), f"Missing validator: {name}"


def test_no_root_level_duplicate_standards():
    for name in ROOT_DUPLICATE_STANDARDS:
        assert not os.path.exists(os.path.join(L1_DIR, name)), (
            f"Root-level duplicate standard found: {name} — must be archived"
        )

REQUIRED_GENERATED = [
    "bootstrap_artifact_manifest.yaml",
    "fic_bundle_manifest.yaml",
    "readiness_report.md",
    "release_candidate_report.md",
    "requirement_coverage_matrix.yaml",
    "review_packet.md",
    "semantic_lockfile.yaml",
    "unit_dag.yaml",
    "validation_report.md",
]

def test_required_generated_files_exist():
    for name in REQUIRED_GENERATED:
        assert os.path.isfile(os.path.join(L1_DIR, "generated", name)), f"Missing generated: {name}"

REQUIRED_L1_DOCS = [
    "00_L1_SYSTEM_GOAL.md",
    "01_L1_BACKGROUND.md",
    "02_L1_ARCHITECTURE_CONTRACT.md",
    "03_L1_WHOLE_SYSTEM_PSEUDOCODE.md",
    "04_L1_UNIT_DAG.md",
    "05_L1_SHARED_TYPES_AND_INTERFACES.md",
    "06_L1_VALIDATION_PLAN.md",
    "07_L1_RISK_LEDGER.md",
    "08_L1_TRACEABILITY_MATRIX.md",
    "09_L1_CODING_AGENT_HANDOFF_RULES.md",
    "10_L1_FAILURE_LEARNING_LOG.md",
    "11_L1_REVIEW_GATE.md",
]

def test_required_l1_docs_exist():
    for name in REQUIRED_L1_DOCS:
        assert os.path.isfile(os.path.join(L1_DIR, "docs", name)), f"Missing L1 doc: {name}"
