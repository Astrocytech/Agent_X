from __future__ import annotations
import json
import re
from pathlib import Path
from agentx_evolve.packaging.packaging_models import (
    DependencyInventory,
    DependencyLockReport,
    PackageManifest,
    VALIDATION_STATUS_PASS,
    VALIDATION_STATUS_WARNING,
    new_id,
    utc_now_iso,
    to_dict,
    write_json_atomic,
)

_VERSION_PIN_RE = re.compile(r"==\s*(\S+)")


def _extract_pinned_dep(dep: str) -> dict | None:
    dep_clean = dep.split(";")[0].split("#")[0].strip()
    m = _VERSION_PIN_RE.search(dep_clean)
    if m:
        name = dep_clean.split("==")[0].strip()
        version = m.group(1).strip().rstrip(",")
        return {"name": name, "version_specifier": f"=={version}", "resolved_version": version}
    parts = dep_clean.split(">=")
    if len(parts) == 2:
        name = parts[0].strip()
        ver = parts[1].strip().split(",")[0].strip()
        return {"name": name, "version_specifier": f">={ver}", "resolved_version": None}
    parts = dep_clean.split("~=")
    if len(parts) == 2:
        name = parts[0].strip()
        ver = parts[1].strip().split(",")[0].strip()
        return {"name": name, "version_specifier": f"~={ver}", "resolved_version": None}
    parts = dep_clean.split("!=")
    if len(parts) == 2:
        name = parts[0].strip()
        return {"name": name, "version_specifier": dep_clean, "resolved_version": None}
    if dep_clean and re.match(r"^[a-zA-Z0-9_.-]+$", dep_clean):
        return {"name": dep_clean, "version_specifier": "", "resolved_version": None}
    return None


def _parse_lock_file_versions(path: Path) -> list[dict]:
    result: list[dict] = []
    name = path.name
    try:
        if name == "poetry.lock":
            import tomllib

            data = tomllib.loads(path.read_text(encoding="utf-8"))
            for pkg in data.get("package", []):
                result.append({
                    "name": pkg.get("name", ""),
                    "version_specifier": f"=={pkg.get('version', '')}",
                    "resolved_version": pkg.get("version", ""),
                })
        elif name == "uv.lock":
            import tomllib

            data = tomllib.loads(path.read_text(encoding="utf-8"))
            for pkg in data.get("package", []):
                result.append({
                    "name": pkg.get("name", ""),
                    "version_specifier": f"=={pkg.get('version', '')}",
                    "resolved_version": pkg.get("version", ""),
                })
        elif name == "Pipfile.lock":
            data = json.loads(path.read_text(encoding="utf-8"))
            for section in ("default", "develop"):
                for pkg_name, info in data.get(section, {}).items():
                    ver = info.get("version", "")
                    if ver.startswith("=="):
                        ver = ver[2:]
                    result.append({
                        "name": pkg_name,
                        "version_specifier": f"=={ver}",
                        "resolved_version": ver,
                    })
        elif path.suffix == ".lock" and "requirements" in name.lower():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith(("#", "-", "//")):
                    continue
                m = _VERSION_PIN_RE.search(line)
                if m:
                    pkg_name = line.split("==")[0].strip()
                    ver = m.group(1).strip()
                    result.append({
                        "name": pkg_name,
                        "version_specifier": f"=={ver}",
                        "resolved_version": ver,
                    })
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to parse lock file: %s", path)
    return result


def _parse_dependency_file_deps(path: Path) -> list[dict]:
    result: list[dict] = []
    name = path.name
    try:
        if name == "pyproject.toml":
            import tomllib

            data = tomllib.loads(path.read_text(encoding="utf-8"))
            for dep in data.get("project", {}).get("dependencies", []):
                entry = _extract_pinned_dep(dep)
                if entry:
                    result.append(entry)
        elif name == "Pipfile":
            import tomllib

            data = tomllib.loads(path.read_text(encoding="utf-8"))
            for section in ("packages", "dev-packages"):
                for pkg_name, spec in data.get(section, {}).items():
                    if isinstance(spec, str):
                        entry = _extract_pinned_dep(f"{pkg_name}{spec}")
                    else:
                        entry = _extract_pinned_dep(pkg_name)
                    if entry:
                        result.append(entry)
        elif name == "setup.cfg":
            text = path.read_text(encoding="utf-8")
            in_requires = False
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("install_requires"):
                    in_requires = True
                    val = stripped.split("=", 1)[1].strip()
                    if val:
                        entry = _extract_pinned_dep(val)
                        if entry:
                            result.append(entry)
                    continue
                if in_requires:
                    if stripped.startswith("[") or (stripped and not stripped.startswith(("#", ";")) and "=" in stripped):
                        in_requires = False
                        continue
                    if stripped and not stripped.startswith("#"):
                        entry = _extract_pinned_dep(stripped)
                        if entry:
                            result.append(entry)
        elif path.suffix == ".txt" or name == "setup.py":
            text = path.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if not stripped or stripped.startswith(("#", "-", "//", "--")):
                    continue
                if re.match(r"^[a-zA-Z0-9_.-]", stripped):
                    entry = _extract_pinned_dep(stripped)
                    if entry:
                        result.append(entry)
    except Exception:
        import logging
        logging.getLogger(__name__).exception("Failed to parse dependency file: %s", path)
    return result


def write_dependency_inventory(
    repo_root: Path,
    manifest: PackageManifest,
    dependency_lock_report: DependencyLockReport,
    output_path: Path,
) -> DependencyInventory:
    dep_files = _find_files(repo_root, ["pyproject.toml", "requirements*.txt", "setup.cfg", "setup.py", "Pipfile"])
    lock_files = _find_files(repo_root, ["poetry.lock", "uv.lock", "requirements*.lock", "Pipfile.lock"])

    resolved: list[dict] = []
    for lf in lock_files:
        resolved.extend(_parse_lock_file_versions(lf))
    if not resolved:
        for df in dep_files:
            for dep in _parse_dependency_file_deps(df):
                if dep not in resolved:
                    resolved.append(dep)

    dep_file_names = sorted({str(f.relative_to(repo_root)) for f in dep_files})
    lock_file_names = sorted({str(f.relative_to(repo_root)) for f in lock_files})

    seen_names: set[str] = set()
    deduped: list[dict] = []
    for dep in resolved:
        name = dep.get("name", "")
        if name and name not in seen_names:
            seen_names.add(name)
            deduped.append(dep)

    inventory = DependencyInventory(
        inventory_id=new_id("dii"),
        created_at=utc_now_iso(),
        dependency_files=dep_file_names,
        lock_files=lock_file_names,
        resolved_dependencies=deduped,
        unpinned_dependencies=dependency_lock_report.unpinned_dependencies,
        network_resolution_used=False,
        status=VALIDATION_STATUS_PASS,
    )

    write_json_atomic(output_path, to_dict(inventory))
    return inventory


def _find_files(repo_root: Path, patterns: list[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(sorted(repo_root.glob(pattern)))
    return found
