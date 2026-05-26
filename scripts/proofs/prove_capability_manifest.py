"""Prove capability manifest — validate CAPABILITY_MANIFEST.yaml structure."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "CAPABILITY_MANIFEST.yaml"
INVARIANTS_PATH = ROOT / "SEED_INVARIANTS.yaml"


def load_yaml(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main() -> int:
    manifest = load_yaml(MANIFEST_PATH)
    invariants = load_yaml(INVARIANTS_PATH)

    errors: list[str] = []

    # Check kernel capabilities
    for cap in manifest.get("kernel_capabilities", []):
        if not cap.get("id"):
            errors.append("kernel_capability missing 'id'")
        if not cap.get("description"):
            errors.append(f"kernel_capability '{cap.get('id', '?')}' missing 'description'")
        if not cap.get("proof_command"):
            errors.append(f"kernel_capability '{cap.get('id', '?')}' missing 'proof_command'")

    # Check blocked capabilities
    for cap in manifest.get("blocked_capabilities", []):
        if not cap.get("id"):
            errors.append("blocked_capability missing 'id'")
        if not cap.get("description"):
            errors.append(f"blocked_capability '{cap.get('id', '?')}' missing 'description'")
        if not cap.get("enforcement"):
            errors.append(f"blocked_capability '{cap.get('id', '?')}' missing 'enforcement'")
        if not cap.get("blocked_by"):
            errors.append(f"blocked_capability '{cap.get('id', '?')}' missing 'blocked_by'")

    # Check extension capability rules
    ext_rules = manifest.get("extension_capability_rules", {})
    required_fields = set(ext_rules.get("required_fields", []))
    allowed_ports = set(ext_rules.get("allowed_attached_ports", []))
    forbidden_l0 = set(ext_rules.get("forbidden_in_l0", []))

    if not required_fields:
        errors.append("extension_capability_rules missing 'required_fields'")

    # Check extension capabilities (should be empty in L0)
    seen_ids: set[str] = set()
    for cap in manifest.get("extension_capabilities", []):
        if not cap.get("id"):
            errors.append("extension_capability missing 'id'")
            continue
        cid = cap["id"]
        if cid in seen_ids:
            errors.append(f"duplicate extension capability id: {cid}")
        seen_ids.add(cid)

        for field in required_fields:
            if field not in cap or cap.get(field) is None:
                errors.append(f"extension_capability '{cid}' missing required field: {field}")

        port = cap.get("attached_port", "")
        if port and port not in allowed_ports:
            errors.append(f"extension_capability '{cid}' attaches to disallowed port: {port}")

        ctype = cap.get("type", "")
        if ctype == "":
            pass
        elif ctype == "tool":
            pass
        elif ctype in forbidden_l0:
            errors.append(f"extension_capability '{cid}' uses forbidden L0 name: {ctype}")

    # Check duplicate ids across all sections
    all_ids: set[str] = set()
    for cap in manifest.get("kernel_capabilities", []):
        cid = cap.get("id")
        if cid:
            if cid in all_ids:
                errors.append(f"duplicate capability id across sections: {cid}")
            all_ids.add(cid)
    for cap in manifest.get("blocked_capabilities", []):
        cid = cap.get("id")
        if cid:
            if cid in all_ids:
                errors.append(f"duplicate capability id across sections: {cid}")
            all_ids.add(cid)
    for cap in manifest.get("extension_capabilities", []):
        cid = cap.get("id")
        if cid:
            if cid in all_ids:
                errors.append(f"duplicate capability id across sections: {cid}")
            all_ids.add(cid)

    # Cross-check against SEED_INVARIANTS allowed attachment points
    inv_ext = invariants.get("extension_boundary", {})
    inv_ports = set(inv_ext.get("allowed_extension_attachment_points", []))
    if inv_ports and allowed_ports != inv_ports:
        errors.append(
            f"CAPABILITY_MANIFEST allowed_ports ({allowed_ports}) "
            f"mismatch SEED_INVARIANTS ({inv_ports})"
        )

    if errors:
        print("CAPABILITY MANIFEST PROOF: FAILED")
        for e in errors:
            print(f"- {e}")
        return 1

    print("CAPABILITY MANIFEST PROOF: OK")
    print(f"- kernel capabilities: {len(manifest.get('kernel_capabilities', []))}")
    print(f"- blocked capabilities: {len(manifest.get('blocked_capabilities', []))}")
    print(f"- extension capabilities: {len(manifest.get('extension_capabilities', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
