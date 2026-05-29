# FIC-L1-002: Repo State Reader

**fic_id:** `FIC-L1-002`
**unit_id:** `UNIT-L1-002`
**version:** `v0.6.0`
**status:** `ready-for-code`
**target_file:** `L1/controller/repo_state_reader.py`

## Description

Provides structured read-only access to repository state. Unlike `document_loader` (which loads arbitrary files at single paths), `repo_state_reader` understands the repository layout, lists files by glob pattern, reads manifest files, and returns structured file metadata.

## Public surface

```python
__all__ = [
    "DEFAULT_MAX_FILE_BYTES",
    "RepoFileInfo",
    "RepoStateReader",
    "RepoStateError",
    "RepoStatePathError",
    "RepoStateReadError",
    "get_repo_file_info",
    "list_repo_files",
    "read_text_file",
]
```

### Exports

- `DEFAULT_MAX_FILE_BYTES: int = 1048576`
- `RepoStateReader` — class with methods:
  - `__init__(self, root: str = ".")` — resolves and validates root directory
  - `list_files(self, glob_pattern: str) -> list[str]` — returns relative POSIX paths
  - `get_file_info(self, path: str) -> RepoFileInfo` — returns file metadata
  - `read_text_file(self, path: str) -> str` — returns UTF-8 content
- `RepoFileInfo` — frozen dataclass: `path`, `relative_path`, `size_bytes`, `sha256`, `is_dir`
- `RepoStateError` — base exception
- `RepoStatePathError` — path validation or traversal errors
- `RepoStateReadError` — read or decode errors
- `get_repo_file_info(path, *, root=".") -> RepoFileInfo`
- `list_repo_files(glob_pattern, *, root=".") -> list[str]`
- `read_text_file(path, *, root=".") -> str`

## Dependency contract

- **stdlib only** (pathlib, hashlib, typing, dataclasses, glob)
- **No** `os`, `subprocess`, `requests`, `urllib`, `socket`, `http`
- **No** imports from `L0` or `L2`

## Rules

1. All paths are relative to the reader root. Absolute paths are rejected.
2. Path traversal outside root is rejected (including symlink escape).
3. `list_files` uses `Path.rglob()` with the given glob pattern.
4. `read_text_file` rejects non-UTF-8 content.
5. `get_file_info` returns SHA-256 digest of raw bytes.
6. All `RepoFileInfo` instances are frozen.
7. Missing files raise `RepoStatePathError`.
8. Files exceeding `DEFAULT_MAX_FILE_BYTES` raise `RepoStateReadError`.
9. The reader does not follow symlinks outside the root.
10. Directories raise `RepoStatePathError` in `read_text_file` and `get_file_info`.

## Edge cases

| Case | Behavior |
|---|---|
| empty string path | `RepoStatePathError` |
| non-string path | `RepoStatePathError` |
| path to non-existent file | `RepoStatePathError` |
| path to directory | `RepoStatePathError` in read/get_file_info |
| symlink to file outside root | `RepoStatePathError` |
| absolute path | `RepoStatePathError` |
| file with no extension | treated as regular file |
| hidden file (dotfile) | listed by rglob |
| empty root | `RepoStatePathError` on init |
| non-existent root | `RepoStatePathError` on init |
| root that is a file | `RepoStatePathError` on init |
| file exceeding max_bytes | `RepoStateReadError` |
| non-UTF-8 file | `RepoStateReadError` |
| glob matching nothing | returns empty list |
| glob matching only dirs | dirs are included in list |
| multiple calls to same path | consistent results |
| `RepoStateReader` instances are independent | each has own root |

## Test contract

Test file: `L1/tests/test_repo_state_reader.py`

Required tests:
1. `test_get_file_info_returns_correct_metadata`
2. `test_get_file_info_computes_sha256`
3. `test_get_file_info_rejects_directory`
4. `test_get_file_info_rejects_missing_file`
5. `test_get_file_info_rejects_absolute_path`
6. `test_get_file_info_rejects_empty_path`
7. `test_get_file_info_rejects_non_string_path`
8. `test_get_file_info_rejects_traversal`
9. `test_get_file_info_rejects_symlink_escape`
10. `test_list_files_matches_glob`
11. `test_list_files_returns_empty_for_no_match`
12. `test_list_files_includes_hidden_files`
13. `test_read_text_file_returns_content`
14. `test_read_text_file_rejects_non_utf8`
15. `test_read_text_file_rejects_oversized`
16. `test_read_text_file_rejects_directory`
17. `test_repo_state_reader_init_rejects_non_existent_root`
18. `test_repo_state_reader_init_rejects_file_root`
19. `test_repo_file_info_is_frozen`
20. `test_repo_state_reader_no_forbidden_imports`
21. `test_read_text_file_returns_sha256`
22. `test_independent_reader_instances`
