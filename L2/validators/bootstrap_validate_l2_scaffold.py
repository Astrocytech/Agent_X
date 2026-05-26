"""L2 bootstrap scaffold validator — checks required structure, no-runtime surface, and profiles."""
import os
import sys

L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO_ROOT = os.path.dirname(L2_DIR)
errors = []
warnings = []

REQUIRED_DOCS = [
    "00_L2_SYSTEM_GOAL.md", "01_L2_BACKGROUND.md", "02_L2_ARCHITECTURE_CONTRACT.md",
    "03_L2_PROFILE_MODEL.md", "04_L2_SPECIALIZATION_CATALOG.md",
    "05_L2_INTEGRATION_BOUNDARIES.md", "06_L2_EVALUATION_PLAN.md",
    "07_L2_RISK_LEDGER.md", "08_L2_TRACEABILITY_MATRIX.md", "09_L2_HANDOFF_TO_L1_RULES.md",
]

REQUIRED_STANDARDS = [
    "AGENT_X_L2_PSEUDOCODE_TO_FIC_WORKFLOW_v0_5.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_FIC_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_SIB_BRIDGE_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_ES_v0_4.md",
    "AGENT_X_L2_LIGHTWEIGHT_EQC_v0_4.md",
]

REQUIRED_PROFILES = [
    "coding_agent.yaml", "symbolic_regression_controller.yaml",
    "research_agent.yaml", "repo_maintenance_agent.yaml",
    "framework_seed.yaml",
]

REQUIRED_BLUEPRINTS = [
    "coding_agent_blueprint.md", "symbolic_regression_controller_blueprint.md",
    "research_agent_blueprint.md", "repo_maintenance_agent_blueprint.md",
    "framework_seed_blueprint.md",
]

REQUIRED_EVALS = [
    "coding_agent_eval.md", "symbolic_regression_eval.md",
    "research_agent_eval.md", "repo_maintenance_eval.md",
    "framework_seed_eval_spec.md",
]

REQUIRED_INTEGRATIONS = [
    "pysr_custom_integration.md", "glyphser_integration.md", "symbiant_integration.md",
]

REQUIRED_FIC_UNITS = [
    "L2-FIC-PROFILE-CODING-001-coding-agent.md",
    "L2-FIC-PROFILE-SR-001-symbolic-regression-controller.md",
    "L2-FIC-PROFILE-RESEARCH-001-research-agent.md",
    "L2-FIC-PROFILE-REPO-001-repo-maintenance-agent.md",
]

PROHIBITED_RUNTIME_DIRS = [
    "controller", "runtime", "agents", "tools", "model_router", "memory", "autonomy",
    "executors", "patchers",
]

def check_path(rel_path):
    full = os.path.join(L2_DIR, rel_path)
    return os.path.exists(full)

def check_required_files(file_list, subdir, label):
    for f in file_list:
        path = os.path.join(subdir, f) if subdir else f
        if not check_path(path):
            errors.append(f"Missing required {label}: {path}")

def check_profile_flag(profile_name, flag):
    path = os.path.join(L2_DIR, "profiles", profile_name)
    if not os.path.isfile(path):
        return
    with open(path) as fh:
        content = fh.read()
    if f"{flag}: true" in content:
        errors.append(f"Profile {profile_name} has {flag}: true")

def check_generated_marker(generated_name):
    path = os.path.join(L2_DIR, "generated", generated_name)
    if not os.path.isfile(path):
        warnings.append(f"Generated file not found: {generated_name}")
        return
    with open(path) as fh:
        content = fh.read()
    if "release_evidence: false" not in content and "bootstrap-placeholder-not-release-evidence" not in content:
        warnings.append(f"Generated file {generated_name} missing release_evidence marker")

def check_handoff_map():
    path = os.path.join(L2_DIR, "sib", "sib-l1-handoff-map.yaml")
    if not os.path.isfile(path):
        warnings.append("SIB handoff map not found")
        return
    with open(path) as fh:
        content = fh.read()
    if "implementation_allowed_by_l2: true" in content:
        errors.append("SIB handoff map has implementation_allowed_by_l2: true")

def check_prohibited_runtime():
    for d in PROHIBITED_RUNTIME_DIRS:
        full = os.path.join(L2_DIR, d)
        if os.path.isdir(full):
            for root, dirs, files in os.walk(full):
                for f in files:
                    if f.endswith((".py", ".sh", ".js", ".ts")):
                        errors.append(f"Executable file in prohibited runtime dir: {os.path.join(root, f)}")

def check_eqc_runtime_authority():
    eqc_dirs = [
        os.path.join(L2_DIR, "eqc", "procedures"),
        os.path.join(L2_DIR, "eqc", "operators"),
    ]
    for d in eqc_dirs:
        if not os.path.isdir(d):
            continue
        for f in os.listdir(d):
            if f.endswith((".eqc.md", ".md")):
                fp = os.path.join(d, f)
                with open(fp) as fh:
                    content = fh.read()
                if "Runtime Authority: granted" in content or "Implementation Authority: granted" in content:
                    errors.append(f"EQC file {f} claims runtime/implementation authority")

def run_checks():
    # Import profile validator and check all profiles
    sys.path.insert(0, REPO_ROOT)
    try:
        from L2.validators.validate_target_profiles import validate_profiles
        profile_errors = validate_profiles(
            profile_dir=os.path.join(L2_DIR, "profiles"),
            taxonomy_path=os.path.join(REPO_ROOT, "L1", "target_taxonomy.yaml"),
        )
        for e in profile_errors:
            errors.append(f"PROFILE: {e}")
    except ImportError as exc:
        warnings.append(f"Profile validator import failed: {exc}")
    finally:
        sys.path.pop(0)

    check_required_files(REQUIRED_DOCS, "docs", "L2 doc")
    check_required_files(REQUIRED_STANDARDS, "standards", "L2 standard")
    check_required_files(REQUIRED_PROFILES, "profiles", "L2 profile")
    check_required_files(REQUIRED_BLUEPRINTS, "blueprints", "L2 blueprint")
    check_required_files(REQUIRED_EVALS, "evaluation_specs", "L2 evaluation spec")
    check_required_files(REQUIRED_INTEGRATIONS, "integration_specs", "L2 integration spec")

    fic_unit_dir = os.path.join("fic", "units")
    check_required_files(REQUIRED_FIC_UNITS, fic_unit_dir, "L2 FIC unit")

    for p in REQUIRED_PROFILES:
        check_profile_flag(p, "implementation_allowed")
        check_profile_flag(p, "direct_runtime_allowed")

    for g in ["profile_catalog.yaml", "l2_profile_package_manifest.yaml",
              "l2_semantic_lockfile.yaml", "readiness_report.md", "validation_report.md",
              "l2_eqc_validator_input_manifest.yaml"]:
        check_generated_marker(g)

    check_handoff_map()
    check_prohibited_runtime()
    check_eqc_runtime_authority()

    print(f"Errors: {len(errors)}")
    for e in errors:
        print(f"  ERROR: {e}")
    print(f"Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  WARNING: {w}")

    if errors:
        sys.exit(1)
    if warnings:
        print("=== bootstrap-validate-l2-scaffold: WARNING ===")
        sys.exit(0)
    print("=== bootstrap-validate-l2-scaffold: PASS ===")

if __name__ == "__main__":
    run_checks()
