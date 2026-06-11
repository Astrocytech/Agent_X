from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def parse_report_dir() -> Path:
    for i, arg in enumerate(sys.argv):
        if arg == "--report-dir" and i + 1 < len(sys.argv):
            return Path(sys.argv[i + 1])
    return Path(".agentx-init/reports")


def load_json(path: str) -> dict | list | None:
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return data
    except (OSError, json.JSONDecodeError):
        return None


# ---------------------------------------------------------------------------
# Coverage decision constants for domain-to-bundle mappings
# ---------------------------------------------------------------------------

# Sentinel: domain is covered by an explicit manual check in this validator
COVERED_BY_MANUAL_CHECK = "COVERED_BY_MANUAL_CHECK"
# Sentinel: domain is covered by a different validator (linked elsewhere)
COVERED_BY_OTHER_VALIDATOR = "COVERED_BY_OTHER_VALIDATOR"
# Sentinel: domain is intentionally out of scope for the current classification
OUT_OF_SCOPE = "OUT_OF_SCOPE"
# Sentinel: domain is known but not yet implementable
BLOCKED = "BLOCKED"


def is_bundle_key(val: object) -> bool:
    """True if *val* is a plain bundle-key string (not a sentinel)."""
    if not isinstance(val, str):
        return False
    return val not in (
        COVERED_BY_MANUAL_CHECK,
        COVERED_BY_OTHER_VALIDATOR,
        OUT_OF_SCOPE,
        BLOCKED,
    )


# ---------------------------------------------------------------------------
# Gap list loading and validation
# ---------------------------------------------------------------------------

_GAP_LIST_FILE = "gap_list.txt"

_GAP_ITEMS_CACHE: list[dict] | None = None


def _resolve_gap_list() -> Path:
    """Return the path to the gap list file stored in the validators directory."""
    return Path(__file__).resolve().parent / _GAP_LIST_FILE


def _validate_gap_list() -> list[str]:
    """Validate the gap list: non-empty, schema, ID ranges, no duplicates."""
    errs: list[str] = []
    path = _resolve_gap_list()
    if not path.exists():
        errs.append(f"gap list file not found at {path}")
        return errs
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        errs.append(f"gap list read error: {e}")
        return errs

    lines = text.split("\n")
    if not lines:
        errs.append("gap list file is empty")
        return errs

    seen_ids: set[int] = set()
    last_id = 0
    for lineno, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line:
            continue
        m = re.match(r"^(\d+)\.\s+(.*)", line)
        if not m:
            errs.append(f"gap list line {lineno}: malformed (does not match N. text)")
            continue
        iid = int(m.group(1))
        if iid in seen_ids:
            errs.append(f"gap list line {lineno}: duplicate ID {iid}")
        seen_ids.add(iid)
        if iid < last_id:
            errs.append(f"gap list line {lineno}: out-of-order ID {iid} after {last_id}")
        last_id = iid

    if not seen_ids:
        errs.append("gap list contains no valid items")
        return errs

    min_id = min(seen_ids)
    max_id = max(seen_ids)
    for expected in range(min_id, max_id + 1):
        if expected not in seen_ids:
            errs.append(f"gap list missing ID {expected}")

    return errs


def _load_gap_items() -> list[dict]:
    global _GAP_ITEMS_CACHE
    if _GAP_ITEMS_CACHE is not None:
        return _GAP_ITEMS_CACHE
    _GAP_ITEMS_CACHE = []
    path = _resolve_gap_list()
    if not path.exists():
        return _GAP_ITEMS_CACHE
    try:
        text = path.read_text(encoding="utf-8")
        for line in text.split("\n"):
            line = line.strip()
            if not line:
                continue
            m = re.match(r"^(\d+)\.\s+(.*)", line)
            if m:
                _GAP_ITEMS_CACHE.append({"id": int(m.group(1)), "text": m.group(2)})
    except OSError:
        pass
    return _GAP_ITEMS_CACHE


def _extract_domain(item_text: str) -> str:
    m = re.match(r"^(.+?)\s+must\s+\w+", item_text)
    if m:
        return m.group(1).strip()
    return item_text.split(".")[0].strip()


def _extract_condition(item_text: str, domain: str) -> str:
    rest = item_text[len(domain):].strip()
    rest = re.sub(r"^proof\s+", "", rest)
    rest = re.sub(r"^must\s+", "", rest)
    return rest[:60].strip()


def _domain_to_bundle_key(domain: str, known_keys: dict | None = None) -> object:
    if known_keys is None:
        return None
    key = domain.lower().replace(" ", "_")
    return known_keys.get(key)


# ---------------------------------------------------------------------------
# Coverage report generator — maps each gap item ID to its decision
# ---------------------------------------------------------------------------

CoverageRecord = dict[str, object]

def generate_coverage_report(
    validators: list[tuple[str, int, int, dict]],
) -> list[CoverageRecord]:
    """Produce a flat list of coverage records, one per gap item.

    Each record contains:
      id, text, domain, validator_label, bundle_key_or_sentinel, coverage_status
    """
    items = _load_gap_items()
    records: list[CoverageRecord] = []
    seen_item_ids: set[int] = set()

    for label, start_id, end_id, mapping in validators:
        for item in items:
            iid = item["id"]
            if not (start_id <= iid <= end_id):
                continue

            if iid in seen_item_ids:
                continue
            seen_item_ids.add(iid)

            txt = item["text"]
            domain = _extract_domain(txt)
            mapped = _domain_to_bundle_key(domain, mapping)

            if mapped is None:
                status = "UNMAPPED"
                bundle_key = ""
            elif mapped == COVERED_BY_MANUAL_CHECK:
                status = "MANUAL_CHECK"
                bundle_key = ""
            elif mapped == COVERED_BY_OTHER_VALIDATOR:
                status = "OTHER_VALIDATOR"
                bundle_key = ""
            elif mapped == OUT_OF_SCOPE:
                status = "OUT_OF_SCOPE"
                bundle_key = ""
            elif mapped == BLOCKED:
                status = "BLOCKED"
                bundle_key = ""
            else:
                status = "BUNDLE_KEY"
                bundle_key = str(mapped)

            records.append({
                "id": iid,
                "text": txt,
                "domain": domain,
                "validator": label,
                "bundle_key": bundle_key,
                "status": status,
            })

    return records


# ---------------------------------------------------------------------------
# Per-item gap coverage checker
# ---------------------------------------------------------------------------

def check_all_gap_items(
    errors: list,
    bundle: object,
    label: str,
    start_id: int,
    end_id: int,
    domain_to_bundle: dict | None = None,
) -> None:
    items = _load_gap_items()
    if not items:
        gap_path = _resolve_gap_list()
        if not gap_path.exists():
            errors.append(f"{label}: gap list file not found at {gap_path}")
        else:
            errors.append(f"{label}: gap list file empty at {gap_path}")
        return

    if not isinstance(bundle, dict):
        errors.append(f"{label}: proof bundle is missing or not a dict — cannot check per-item coverage")
        return

    # Group by bundle_key
    domain_groups: dict[str, dict] = {}
    for item in items:
        iid = item["id"]
        if not (start_id <= iid <= end_id):
            continue
        txt = item["text"]
        domain = _extract_domain(txt)
        mapped = _domain_to_bundle_key(domain, domain_to_bundle)

        if mapped is None:
            errors.append(
                f"{label}: {iid} - {domain} has no mapping "
                f"(add to domain_to_bundle or mark with a sentinel)"
            )
            continue

        # Sentinel values
        if mapped == COVERED_BY_MANUAL_CHECK:
            continue
        if mapped == COVERED_BY_OTHER_VALIDATOR:
            continue
        if mapped == OUT_OF_SCOPE:
            continue
        if mapped == BLOCKED:
            continue

        if not is_bundle_key(mapped):
            errors.append(
                f"{label}: {iid} - {domain} has invalid mapping value {mapped!r}"
            )
            continue

        bundle_key: str = mapped
        if bundle_key not in domain_groups:
            domain_groups[bundle_key] = {"domain": domain, "items": []}
        domain_groups[bundle_key]["items"].append(item)

    # Check each domain group against the bundle
    for bundle_key, group in domain_groups.items():
        group_items = group["items"]
        domain = group["domain"]
        ids = [item["id"] for item in group_items]
        first_id = min(ids)
        last_id = max(ids)
        id_range_str = f"{first_id}-{last_id}" if first_id != last_id else str(first_id)

        if bundle_key not in bundle:
            errors.append(
                f"{label}: {id_range_str} - {domain} metadata missing "
                f"(expected bundle key: {bundle_key}, covers items {', '.join(str(i) for i in ids)})"
            )
        elif isinstance(bundle[bundle_key], dict):
            for item in group_items:
                iid = item["id"]
                txt = item["text"]
                condition = _extract_condition(txt, domain)
                if condition:
                    sub_key = condition.lower().replace(" ", "_").replace("-", "_")[:40]
                    sub_key = re.sub(r"[^a-z0-9_]", "", sub_key)
                    if sub_key and sub_key not in bundle[bundle_key]:
                        errors.append(
                            f"{label}: {iid} - {domain} missing sub-field "
                            f"'{sub_key}' in {bundle_key}"
                        )
