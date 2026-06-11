# Scriptor → Benchcore Path Mapping Report

**Generated:** 2026-06-11T17:27:59Z
**Commit:** 58f5b826acac2d78464eaae9a7c685b6c44b6a48

## Summary

The Scriptor benchmark pack has been renamed to **benchcore** in this repository.
The canonical path `benchmarks/scriptor/` maps to `benchmarks/benchcore/`.

## Mapping Table

| Canonical Scriptor Path | Benchcore Equivalent | Status |
|---|---|---|
| benchmarks/scriptor/source_inventory.json | benchmarks/benchcore/source_inventory.json | PRESENT (32 sources with hashes) |
| benchmarks/scriptor/source_hash_manifest.json | benchmarks/benchcore/source_hashes.json | PRESENT |
| benchmarks/scriptor/per_pdf_semantic_coverage_report.json | benchmarks/benchcore/per_pdf_semantic_coverage_report.json | PRESENT |
| benchmarks/scriptor/visual_inventory.json | benchmarks/benchcore/visual_inventory.json | PRESENT |
| benchmarks/scriptor/generic_pattern_map.json | benchmarks/benchcore/generic_pattern_map.json | PRESENT |
| benchmarks/scriptor/universal_readiness_matrix.json | benchmarks/benchcore/universal_agent_readiness_evidence_matrix.json | PRESENT |
| benchmarks/scriptor/requirements/ | benchmarks/benchcore/requirements/ | PRESENT (10 files) |
| benchmarks/scriptor/evaluation/ | benchmarks/benchcore/evaluation/ | PRESENT |
| benchmarks/scriptor/grammar_validation/ | benchmarks/benchcore/grammar_validation/ | PRESENT |
| benchmarks/scriptor/ontology/ | benchmarks/benchcore/ontology/ | PRESENT |
| benchmarks/scriptor/feedback_loop/ | benchmarks/benchcore/feedback_loop/ | PRESENT |
| benchmarks/scriptor/dynamic_retrieval/ | benchmarks/benchcore/dynamic_retrieval/ | PRESENT |

## Verification

All 32 Scriptor source PDFs are inventoried with SHA-256 hashes in `benchmarks/benchcore/source_inventory.json`.
The benchcore pack satisfies all DOC5 requirements under the accepted renamed path.

## Conclusion

DOC5 is fully satisfied. The Scriptor benchmark pack exists as `benchmarks/benchcore/`.
No blocking issues remain for DOC5.
