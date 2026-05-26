from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.governance_engine import run_governance_checks


def generate_plan() -> list[dict]:
    scan = scan_repo()
    checks = run_governance_checks()
    failed = [c for c in checks if not c["passed"]]
    recommendations = []

    if failed:
        recommendations.append({
            "priority": 1,
            "category": "governance",
            "action": "Resolve governance check failures",
            "detail": f"{len(failed)} checks failed: {[c['check'] for c in failed]}",
        })

    if scan.total_files == 0:
        recommendations.append({
            "priority": 2,
            "category": "structure",
            "action": "Investigate empty repository scan",
            "detail": "No files found during scan",
        })

    recommendations.append({
        "priority": 10,
        "category": "fic",
        "action": "Create unit-level FIC contracts under L1/fic/",
        "detail": "Root governance documents exist; implement UNIT-001 through UNIT-014",
    })

    recommendations.append({
        "priority": 20,
        "category": "validation",
        "action": "Implement validators for L1 governance",
        "detail": "Bootstrap formal validators for FIC contracts, schemas, and digests",
    })

    recommendations.append({
        "priority": 30,
        "category": "specialization",
        "action": "Select and develop L2 profile for implementation",
        "detail": "Most likely first candidate: L2-PROFILE-SR-001 Symbolic Regression Controller",
    })

    return recommendations
