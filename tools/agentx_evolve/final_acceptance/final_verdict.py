from .acceptance_models import (
    CrossLayerCheck, FinalAcceptanceEvidenceManifest, FinalAcceptanceDeviation,
    FinalAcceptanceValidationResult,
    VERDICT_ACCEPTED, VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, VERDICT_NOT_ACCEPTED,
    STATUS_FAIL, STATUS_PASS, STATUS_PARTIAL, STATUS_NOT_CHECKED,
    STATUS_NOT_RUN, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY, STATUS_STALE,
    SEVERITY_BLOCKER, SEVERITY_HIGH,
)


def _verdict_from_blockers_high(blockers: list[str], high_issues: list[str]) -> str:
    if blockers:
        return VERDICT_NOT_ACCEPTED
    if high_issues:
        return VERDICT_NOT_ACCEPTED
    return VERDICT_ACCEPTED


def calculate_final_verdict(
    evidence_manifest: FinalAcceptanceEvidenceManifest | None = None,
    cross_layer_checks: list[CrossLayerCheck] | None = None,
    validation_results: list[FinalAcceptanceValidationResult] | None = None,
    schema_validation_results: list[FinalAcceptanceValidationResult] | None = None,
    deviations: list[FinalAcceptanceDeviation] | None = None,
    layer_statuses: dict[str, str] | None = None,
    safe_deferrals: list[dict] | None = None,
    blockers: list[str] | None = None,
    high_issues: list[str] | None = None,
    non_blocking_followups: list[str] | None = None,
    bootstrap_self: bool = False,
    no_safe_deferrals: bool = False,
) -> tuple[str, float, list[str], list[str], list[str]]:
    blockers = blockers or []
    high_issues = high_issues or []
    non_blocking_followups = non_blocking_followups or []
    safe_deferrals = safe_deferrals or []
    layer_statuses = layer_statuses or {}

    test_failures = 0
    blocker_count = len(blockers)
    high_count = len(high_issues)
    deferral_count = len(safe_deferrals)

    if evidence_manifest:
        for item in evidence_manifest.items:
            if item.required and item.exists and not item.readable:
                issue = f"Layer {item.layer_id}: {item.artifact_path} exists but unreadable"
                if issue not in blockers:
                    blockers.append(issue)

    required_layers = {
        lid for lid, st in layer_statuses.items()
        if st in (STATUS_FAIL, STATUS_STALE)
    }
    for lid in required_layers:
        issue = f"Required layer {lid} has status FAIL or STALE"
        if issue not in blockers:
            blockers.append(issue)

    if cross_layer_checks:
        for c in cross_layer_checks:
            if c.status == STATUS_FAIL and c.severity == SEVERITY_BLOCKER:
                issue = f"Cross-layer check {c.check_id}: {c.requirement}"
                if issue not in blockers:
                    blockers.append(issue)
            elif c.status == STATUS_FAIL and c.severity == SEVERITY_HIGH:
                issue = f"Cross-layer check {c.check_id}: {c.requirement}"
                if issue not in high_issues:
                    high_issues.append(issue)

    if validation_results:
        for r in validation_results:
            if r.status == STATUS_FAIL:
                issue = f"Validation command {r.command_name} failed: {r.summary}"
                if issue not in high_issues:
                    high_issues.append(issue)
                test_failures += 1

    if schema_validation_results:
        for r in schema_validation_results:
            if r.status == STATUS_FAIL:
                issue = f"Schema validation {r.command_name} failed: {r.summary}"
                if issue not in high_issues:
                    high_issues.append(issue)
                test_failures += 1

    if deviations:
        for d in deviations:
            if d.safety_impact == "critical":
                issue = f"Deviation {d.deviation_id}: critical safety impact"
                if issue not in blockers:
                    blockers.append(issue)

    if no_safe_deferrals and safe_deferrals:
        for sd in safe_deferrals:
            lid = sd.get("layer_id", "unknown")
            issue = f"Safe deferral rejected by --no-safe-deferrals for layer {lid}"
            if issue not in blockers:
                blockers.append(issue)

    blocker_count = len(blockers)
    high_count = len(high_issues)

    if not layer_statuses:
        passed_layers = 1
        total_layers = 1
    else:
        passed_layers = sum(
            1 for st in layer_statuses.values()
            if st in (STATUS_PASS, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY)
        )
        total_layers = len(layer_statuses)
    implementation_rating = passed_layers / total_layers

    if blocker_count > 0:
        return (
            VERDICT_NOT_ACCEPTED, implementation_rating,
            blockers, high_issues, non_blocking_followups,
        )

    if high_count > 0 or test_failures > 0:
        return (
            VERDICT_NOT_ACCEPTED, implementation_rating,
            blockers, high_issues, non_blocking_followups,
        )

    all_accepted = all(
        st in (STATUS_PASS, STATUS_NOT_APPLICABLE, STATUS_DEFERRED_SAFELY)
        for st in layer_statuses.values()
    )

    if all_accepted and safe_deferrals:
        return (
            VERDICT_ACCEPTED_WITH_SAFE_DEFERRALS, implementation_rating,
            blockers, high_issues, non_blocking_followups,
        )
    elif all_accepted:
        return (
            VERDICT_ACCEPTED, implementation_rating,
            blockers, high_issues, non_blocking_followups,
        )

    return (
        VERDICT_NOT_ACCEPTED, implementation_rating,
        blockers, high_issues, non_blocking_followups,
    )
