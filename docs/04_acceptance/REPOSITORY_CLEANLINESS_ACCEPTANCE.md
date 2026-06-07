# Repository Cleanliness Acceptance

## Acceptance Commands

```bash
make audit-structure
pytest --collect-only -q
make test-all
find . -maxdepth 1 -type f | sort
git status --short
```

## Verdict

**PASS** only if:

- no loose planning/review docs exist at root
- no orphan tests exist
- no generated runtime artifacts are tracked
- no live tests run by default
- every major doc has status/owner metadata
- archive contains old revisions only
- active docs point to current implementation
