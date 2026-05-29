# L2 Lightweight ES Standard

## Purpose

EQC-ES at L2 makes profile/spec documents discoverable, version-compatible, and
automatically updatable within the L2 portfolio.

## Registration Rules

1. Every L2 document must be registered in `ecosystem-registry.yaml`.
2. Every document must have a unique `doc_id` prefixed with `AX-L2-`.
3. Document types include: `system-goal`, `profile`, `blueprint`,
   `integration-spec`, `evaluation-spec`, `standard`, `governance-note`.
4. The ecosystem graph must show governance relationships.
5. When a document is updated, the registry status must reflect the change.

## Registry Fields

| Field | Required | Description |
|-------|----------|-------------|
| `doc_id` | Yes | Unique identifier |
| `title` | Yes | Human-readable title |
| `type` | Yes | Document type from allowed list |
| `path` | Yes | Relative path from repo root |
| `version` | Yes | Semantic version |
| `status` | Yes | active, draft, deprecated |
| `layer` | Yes | 0 (constitutional), 1 (standards), 2 (profile) |
| `authority_level` | Yes | constitutional, standard, profile, reference |
