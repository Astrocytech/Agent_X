# L1 Validation Report

Generated-From: L1.validators.validate_all
Generated-At-UTC: 2026-05-29T19:02:23Z
Commit: 775bdc213b053e539e529c6101274009ff95ce8b
Status: WARNING
Release Evidence: false

Commands run:
- python -m compileall -q L1
- pytest L1/tests -q
- python -m L1.validators.validate_all

Validator summary:
- FIC: PASS
- SIB: PASS
- ES: PASS
- EQC: PASS
- Lockfile: WARNING

Errors:
- (none)

Warnings:
- Semantic lockfile status is placeholder — not release evidence
- release_evidence is false — validator must not report release-ready

Skipped checks:
- Digest-based cross-layer consistency (no digest closure implemented yet)

Release evidence rule:
- Use Release Evidence: true only when all release-required checks pass and the semantic lockfile is non-placeholder.
- Otherwise use Release Evidence: false.
