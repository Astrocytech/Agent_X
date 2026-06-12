# Alias: Benchcore / Scriptor

The directory `benchmarks/benchcore/` is the repository-safe name for the
**Scriptor** benchmark pack. All references to "Scriptor" in design documents
and plans resolve to `benchmarks/benchcore/` for implementation.

## Mapping

| Plan name   | Filesystem path              |
|-------------|------------------------------|
| Scriptor    | `benchmarks/benchcore/`      |
| Benchcore   | `benchmarks/benchcore/`      |

## Enforcement

- All internal code, validators, tests, and Makefile targets use `benchcore/`.
- Plans, proposals, and governance documents may use either name.
- The `source_inventory.json` and `source_hash_manifest.json` under `benchcore/`
  are the canonical source-only artifacts for this pack.
- This alias was chosen (Option B of the 50-item work document, item 5.1)
  to avoid the disruption of a physical rename while maintaining plan alignment.
