#!/usr/bin/env python3
"""Gap 13: Validate the authority chain for final classification.

The authoritative classification source is the functional-agentx
final_verdict.json and classification_report.json. Legacy targets
(final-acceptance, generate-final-artifacts) are non-authoritative
and cannot satisfy functional-agentx gates unless imported through
validated evidence refs with explicit 'legacy' metadata.

Also detects conflicting claims between prove-all, legacy
final-acceptance, and prove-functional-agentx.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

FUNCTIONAL_REPORT_DIR = Path(".agentx-init/reports/functional-agentx")
LEGACY_REPORT_DIRS = [
    Path(".agentx-init/reports/final-acceptance"),
    Path(".agentx-init/reports/legacy"),
    Path("reports/legacy-final-acceptance"),
]

LEGACY_MARKER_FILES = [
    "final_verdict.json",
    "final_acceptance.json",
    "classification_report.json",
]

LEGACY_PATHS = [
    ".agentx-init/reports/final-acceptance/",
    ".agentx-init/reports/legacy/",
    "reports/legacy-final-acceptance/",
]


def _path_is_legacy(path: str) -> bool:
    return any(path.startswith(legacy) for legacy in LEGACY_PATHS)


def validate() -> list[str]:
    errors: list[str] = []
    manifest_path = FUNCTIONAL_REPORT_DIR / "evidence_manifest.json"
    auth_verdict = FUNCTIONAL_REPORT_DIR / "final_verdict.json"
    alias_path = FUNCTIONAL_REPORT_DIR / "alias_report.json"

    # 1. The authoritative source must exist
    if not auth_verdict.exists():
        errors.append("Authoritative final_verdict.json not found at functional-agentx")
        return errors

    try:
        auth_data = json.loads(auth_verdict.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as e:
        errors.append(f"Authoritative verdict invalid: {e}")
        return errors

    auth_classification = auth_data.get("classification", "")
    auth_verdict_status = auth_data.get("verdict", "")

    if not auth_classification:
        errors.append("Authoritative verdict has no classification")

    # 2. Consume evidence manifest - check for legacy-stamped refs
    if manifest_path.exists():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for ref in manifest.get("evidence_refs", []):
                ref_path = ref.get("path", "")
                ref_namespace = ref.get("namespace", "")
                ref_origin = ref.get("origin", ref.get("provenance", ""))

                # If a ref points to a legacy path, it MUST have origin=legacy
                if _path_is_legacy(ref_path) and ref_origin != "legacy":
                    errors.append(
                        f"Evidence ref {ref.get('name', '?')} points to legacy path '{ref_path}' "
                        f"but origin is '{ref_origin}', expected 'legacy'"
                    )

                # If origin is legacy, the ref should NOT satisfy canonical
                # functional-agentx namespaces
                if ref_origin == "legacy" and ref_namespace == "functional-agentx":
                    errors.append(
                        f"Evidence ref {ref.get('name', '?')} with origin='legacy' "
                        f"is in namespace 'functional-agentx' — legacy artifacts cannot "
                        f"satisfy canonical gates"
                    )

                # If a ref is in a legacy path but claims canonical status
                if _path_is_legacy(ref_path) and ref.get("canonical_or_alias") == "canonical":
                    errors.append(
                        f"Evidence ref {ref.get('name', '?')} points to legacy path '{ref_path}' "
                        f"but claims canonical status"
                    )
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"evidence_manifest.json invalid: {e}")

    # 3. Verify the authority chain producer
    auth_producer = auth_data.get("producer", "")
    if "generate_functional_agentx_final_verdict" not in auth_producer:
        errors.append(f"Authoritative verdict not from expected producer: {auth_producer}")

    # 4. Check classification_report.json agrees
    class_report = FUNCTIONAL_REPORT_DIR / "classification_report.json"
    if class_report.exists():
        try:
            class_data = json.loads(class_report.read_text(encoding="utf-8"))
            if class_data.get("classification") != auth_classification:
                errors.append("Classification report disagrees with final verdict")
            if class_data.get("verdict") != auth_verdict_status:
                errors.append("Classification report disagrees with final verdict status")
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"Classification report invalid: {e}")

    # 5. Check alias report for legacy-to-canonical aliasing
    if alias_path.exists():
        try:
            alias_data = json.loads(alias_path.read_text(encoding="utf-8"))
            for mapping in alias_data.get("aliases", []):
                source = mapping.get("alias", "")
                target = mapping.get("canonical", "")
                if _path_is_legacy(source) and not target.startswith(".agentx-init/reports/functional-agentx/"):
                    # Legacy path aliased to non-canonical target - not a conflict
                    pass
                if _path_is_legacy(source) and "verdict" in mapping and mapping["verdict"] != auth_verdict_status:
                    errors.append(
                        f"Alias report maps legacy path '{source}' with verdict '{mapping['verdict']}' "
                        f"but authoritative verdict is '{auth_verdict_status}'"
                    )
        except (OSError, json.JSONDecodeError) as e:
            errors.append(f"alias_report.json invalid: {e}")

    # 6. Detect legacy PASS artifacts that might satisfy gates by path coincidence
    for legacy_dir in LEGACY_REPORT_DIRS:
        if not legacy_dir.exists():
            continue
        for fname in LEGACY_MARKER_FILES:
            legacy_path = legacy_dir / fname
            if not legacy_path.exists():
                continue
            try:
                legacy_data = json.loads(legacy_path.read_text(encoding="utf-8"))
                legacy_verdict = legacy_data.get("verdict", legacy_data.get("status", ""))
                legacy_classification = legacy_data.get("classification", "")

                # Legacy PASS with same classification as authoritative creates conflicting claim
                if legacy_verdict == "PASS" and legacy_classification:
                    if legacy_classification == auth_classification or (
                        auth_classification == "FUNCTIONAL_AGENTX_COMPLETE" and legacy_classification in (
                            "FUNCTIONAL_AGENTX_COMPLETE", "FUNCTIONAL_GOVERNED_SELF_EVOLUTION_PROTOTYPE"
                        )
                    ):
                        # Check if this legacy path is aliased in evidence manifest
                        aliased_in_manifest = False
                        if manifest_path.exists():
                            try:
                                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                                for ref in manifest.get("evidence_refs", []):
                                    if _path_is_legacy(ref.get("path", "")) and ref.get("origin") == "legacy":
                                        aliased_in_manifest = True
                                        break
                            except (OSError, json.JSONDecodeError):
                                pass
                        if not aliased_in_manifest:
                            errors.append(
                                f"Legacy report at {legacy_path} has PASS/classification '{legacy_classification}' "
                                f"matching authoritative, but not imported through evidence manifest refs — "
                                f"creates conflicting claim"
                            )
            except (OSError, json.JSONDecodeError):
                continue

    return errors


def main() -> int:
    errs = validate()
    passed = len(errs) == 0
    result = {
        "validator": "validate_authority_chain",
        "passed": passed,
        "errors": errs,
        "summary": "PASS" if passed else "FAIL",
    }
    result_path = FUNCTIONAL_REPORT_DIR / "validate_authority_chain.json"
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")

    if errs:
        print("VALIDATE AUTHORITY CHAIN FAILED:")
        for e in errs:
            print(f"  - {e}")
        return 1
    print("validate-authority-chain: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
