from __future__ import annotations
import re
from pathlib import Path
from agentx_evolve.packaging.packaging_models import (
    DependencyLockReport,
    PackageManifest,
    VALIDATION_STATUS_BLOCKED,
    VALIDATION_STATUS_FAIL,
    VALIDATION_STATUS_NOT_CHECKED,
    VALIDATION_STATUS_PASS,
    new_id,
    utc_now_iso,
)

_PIN_RE = re.compile(r"==\s*\d")


def find_dependency_files(repo_root: Path) -> list[Path]:
    found: list[Path] = []
    for pattern in ("pyproject.toml", "requirements*.txt", "setup.cfg", "setup.py", "Pipfile"):
        found.extend(sorted(repo_root.glob(pattern)))
    return found


def find_lock_files(repo_root: Path) -> list[Path]:
    found: list[Path] = []
    for pattern in ("poetry.lock", "uv.lock", "requirements*.lock", "Pipfile.lock"):
        found.extend(sorted(repo_root.glob(pattern)))
    return found


def _parse_pyproject_deps(path: Path) -> list[str]:
    try:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return []
    project = data.get("project", {})
    deps: list[str] = project.get("dependencies", []) or []
    return [d.strip() for d in deps]


def _parse_requirements_deps(path: Path) -> list[str]:
    deps: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return deps
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-", "//", "--")):
            continue
        if re.match(r"^[a-zA-Z0-9_.-]", line):
            deps.append(line)
    return deps


def _parse_setup_cfg_deps(path: Path) -> list[str]:
    deps: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except Exception:
        return deps
    in_requires = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("install_requires"):
            in_requires = True
            val = stripped.split("=", 1)[1].strip()
            if val:
                deps.append(val)
            continue
        if in_requires:
            if stripped.startswith("[") or (stripped and not stripped.startswith(("#", ";")) and "=" in stripped):
                in_requires = False
                continue
            if stripped and not stripped.startswith("#"):
                deps.append(stripped)
    return deps


def _parse_pipfile_deps(path: Path) -> list[str]:
    deps: list[str] = []
    try:
        import tomllib

        data = tomllib.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return deps
    for section in ("packages", "dev-packages"):
        for pkg_name, spec in data.get(section, {}).items():
            if isinstance(spec, str):
                deps.append(f"{pkg_name}{spec}")
            else:
                deps.append(pkg_name)
    return deps


def _is_unpinned(dep: str) -> bool:
    if not dep:
        return False
    name_part = dep.split(";")[0].split("#")[0].strip()
    if not name_part:
        return False
    if name_part.startswith("-") or name_part.startswith("#"):
        return False
    if re.match(r"^[a-zA-Z0-9_.-]+$", name_part):
        return True
    return not bool(_PIN_RE.search(name_part))


def detect_unpinned_dependencies(path: Path) -> list[str]:
    name = path.name
    if name == "pyproject.toml":
        deps = _parse_pyproject_deps(path)
    elif name == "Pipfile":
        deps = _parse_pipfile_deps(path)
    elif name == "setup.cfg":
        deps = _parse_setup_cfg_deps(path)
    elif path.suffix == ".txt" or path.suffix == ".lock" or name == "setup.py":
        deps = _parse_requirements_deps(path)
    else:
        deps = _parse_requirements_deps(path)
    return [d for d in deps if _is_unpinned(d)]


def validate_dependency_lock(
    repo_root: Path,
    manifest: PackageManifest,
) -> DependencyLockReport:
    dep_files = find_dependency_files(repo_root)
    lock_files = find_lock_files(repo_root)

    unpinned: list[str] = []
    for df in dep_files:
        unpinned.extend(detect_unpinned_dependencies(df))

    lock_file_names = [str(lf.relative_to(repo_root)) for lf in lock_files]
    dep_file_names = [str(df.relative_to(repo_root)) for df in dep_files]

    report = DependencyLockReport(
        report_id=new_id("dlr"),
        created_at=utc_now_iso(),
        lock_files_found=lock_file_names,
        lock_files_required=[],
        missing_lock_files=[],
        dependency_files_found=dep_file_names,
        unpinned_dependencies=sorted(set(unpinned)),
        status=VALIDATION_STATUS_PASS,
    )

    if manifest.require_dependency_lock:
        expected_locks = ["poetry.lock", "uv.lock", "requirements.lock", "Pipfile.lock"]
        lock_found_names = {lf.name for lf in lock_files}
        required: list[str] = []
        missing: list[str] = []
        for el in expected_locks:
            required.append(el)
            if el not in lock_found_names:
                missing.append(el)
        report.lock_files_required = required
        report.missing_lock_files = missing
        if missing:
            report.status = VALIDATION_STATUS_BLOCKED
        elif unpinned:
            report.status = VALIDATION_STATUS_FAIL
        else:
            report.status = VALIDATION_STATUS_PASS
    elif unpinned:
        report.status = VALIDATION_STATUS_FAIL

    return report
