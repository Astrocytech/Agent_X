# Contributing

## Where tests go

- Component tests live inside the component's `tests/` directory.
- Cross-component tests go to `tests/integration/`.
- Full CLI workflow tests go to `tests/system/`.
- Regression tests go to `tests/regression/`.
- Quick import/help tests go to `tests/smoke/`.

## Where docs go

- Project-wide docs go to `docs/` with subfolder by topic.
- Layer-specific docs live inside the layer.
- Tool-specific docs live inside the tool's `docs/` directory.

## Naming rules

- Test files: `test_<component>__<behavior>.py`
- Schema files: `<name>.schema.json`
- Source files: `snake_case.py`
- Document files: `UPPER_SNAKE_CASE.md`

## Fixtures

Fixtures go to `<owner>/fixtures/`. Do not mix fixtures with tests or docs.

## Schemas

Schemas go to `<owner>/schemas/`. Do not put schema files inside test directories.

## Archive old docs

Old REV documents and superseded plans go to `docs/05_archive/superseded_runtime_docs/`.

## Required commands before commit

```bash
make audit-structure
pytest --collect-only -q
make test-all
```

Ensure `git status --short` shows only intentional changes — no generated runtime artifacts.
