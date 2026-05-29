"""ES validator — checks ecosystem sidecars and schemas."""

from pathlib import Path

from L1.validators.common import (
    ValidationResult, check_file, check_dir, check_nonempty, load_yaml,
)

REQUIRED_ES_FILES = [
    "L1/ecosystem/ecosystem-registry.yaml",
    "L1/ecosystem/ecosystem-graph.yaml",
    "L1/ecosystem/ecosystem-error-codes.yaml",
    "L1/ecosystem/ecosystem-validation-log.md",
    "L1/ecosystem/ecosystem-waivers.yaml",
    "L1/ecosystem/ecosystem-migration-log.md",
]

ES_SCHEMAS_DIR = "L1/ecosystem/ecosystem-schemas/"
BASE = Path(__file__).resolve().parent.parent


def validate() -> ValidationResult:
    r = ValidationResult(name="ES")

    for path in REQUIRED_ES_FILES:
        err = check_nonempty(path)
        if err:
            r.errors.append(err)
            r.status = "BLOCKED"

    err = check_dir(ES_SCHEMAS_DIR)
    if err:
        r.errors.append(err)
        r.status = "BLOCKED"
    else:
        schemas = list((BASE / "ecosystem" / "ecosystem-schemas").glob("*.json"))
        if not schemas:
            r.errors.append("ES schemas directory contains no JSON schema files")
            r.status = "BLOCKED"

    registry = load_yaml("L1/ecosystem/ecosystem-registry.yaml")
    if registry:
        docs = registry.get("documents", [])
        known_doc_ids = set()
        for doc in docs:
            doc_id = doc.get("doc_id", "")
            if doc_id:
                known_doc_ids.add(doc_id)
            path = doc.get("path", "")
            if path:
                err = check_file(path)
                if err:
                    r.errors.append(f"ES registry doc {doc_id}: {err}")
                    r.status = "WARNING"

        graph = load_yaml("L1/ecosystem/ecosystem-graph.yaml")
        if graph:
            for edge in graph.get("edges", []):
                src = edge.get("src", "")
                dst = edge.get("dst", "")
                if src and src not in known_doc_ids:
                    r.warnings.append(f"ES graph edge src '{src}' not in registry doc_ids")
                if dst and dst not in known_doc_ids:
                    r.warnings.append(f"ES graph edge dst '{dst}' not in registry doc_ids")

    return r
