#!/usr/bin/env python3
import json, sys, os

ALLOWED_STATUSES = {
    "PASS", "FAIL", "PARTIAL", "SCAFFOLD_ONLY", "MISSING", "BLOCKED",
    "CONFLICT", "UNKNOWN", "UNVERIFIED", "WEAK_TARGET", "NOT_RUN",
    "COMMAND_MISSING", "PLACEHOLDER", "NOT_APPLICABLE_WITH_REASON",
}

REQUIRED_REQ_FIELDS = {"id", "source_document", "status"}
PASS_SUBSTANTIATION_FIELDS = {"implementation_files", "test_files"}

KNOWN_SOURCE_DOCUMENTS = {"DOC1", "DOC2", "DOC3", "DOC4", "DOC5"}

SOURCE_DOC_NAMES = {
    "DOC1": "Coverage Completion",
    "DOC2": "Umbrella Agent Milestone",
    "DOC3": "Post-Umbrella Phase",
    "DOC4": "Inverse Science Method",
    "DOC5": "Scriptor Integration",
}


def validate(path: str) -> list[str]:
    errors = []
    with open(path) as f:
        data = json.load(f)

    if "requirements" not in data or not isinstance(data["requirements"], list):
        errors.append("Missing or invalid 'requirements' array")
        return errors

    reqs = data["requirements"]

    covered_docs = set()
    seen_ids = set()

    for i, req in enumerate(reqs):
        if not isinstance(req, dict):
            errors.append(f"Requirement at index {i} is not a dict")
            continue

        rid = req.get("id", f"req-{i}")
        if rid in seen_ids:
            errors.append(f"{rid}: duplicate requirement id")
        seen_ids.add(rid)

        for field in REQUIRED_REQ_FIELDS:
            if field not in req:
                errors.append(f"{rid}: missing required field '{field}'")

        if "source_document" in req:
            sd = req["source_document"]
            covered_docs.add(sd)
            if sd not in KNOWN_SOURCE_DOCUMENTS:
                errors.append(f"{rid}: unknown source_document '{sd}', expected one of {sorted(KNOWN_SOURCE_DOCUMENTS)}")

        status = req.get("status", "")
        if status not in ALLOWED_STATUSES:
            errors.append(f"{rid}: invalid status '{status}'")
        if status == "UNKNOWN":
            errors.append(f"{rid}: status is UNKNOWN (must be resolved)")

        if status == "PASS":
            for field in PASS_SUBSTANTIATION_FIELDS:
                val = req.get(field)
                if not val or not isinstance(val, list) or len(val) == 0:
                    errors.append(f"{rid}: PASS but '{field}' is empty or missing")

        mandatory = req.get("mandatory", True)
        if mandatory and status in ("MISSING", "BLOCKED", "CONFLICT", "UNKNOWN"):
            errors.append(f"{rid}: mandatory requirement has blocking status '{status}'")

    for doc_id in KNOWN_SOURCE_DOCUMENTS:
        if doc_id not in covered_docs:
            errors.append(f"Source document {doc_id} ({SOURCE_DOC_NAMES[doc_id]}) has no requirements in matrix")

    if len(reqs) < 5:
        errors.append(f"Too few requirements ({len(reqs)}), expected at least 5 for 5 source documents")

    return errors


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else ".agentx-init/five_document_closure/matrix/five_document_traceability_matrix.json"
    if not os.path.exists(path):
        print(f"FAIL: {path} not found")
        sys.exit(1)
    errors = validate(path)
    if errors:
        print(f"FAIL: {len(errors)} validation error(s):")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)
    print(f"PASS: {path} validates (full mandatory closure — {KNOWN_SOURCE_DOCUMENTS} covered, all required fields present)")
    sys.exit(0)


if __name__ == "__main__":
    main()
