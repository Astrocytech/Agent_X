from pathlib import Path
from agentx_initiator.core.repo_model import RepoScan, LayerEntry, FileEntry
from agentx_initiator.core.paths import repo_root


def scan_repo() -> RepoScan:
    root = repo_root()
    layers = []
    total = 0
    source = 0
    doc = 0
    test = 0

    for layer_name in ["L0", "L1", "L2"]:
        layer_path = root / layer_name
        if not layer_path.exists():
            continue
        files = list(layer_path.rglob("*"))
        file_count = len([f for f in files if f.is_file()])
        has_readme = (layer_path / "README.md").exists()
        purpose = _layer_purpose(layer_name)
        layers.append(LayerEntry(
            layer=layer_name,
            path=layer_path,
            purpose=purpose,
            file_count=file_count,
            has_readme=has_readme,
        ))
        total += file_count
        for f in files:
            if f.is_file():
                ext = f.suffix
                if ext in (".py", ".js", ".ts", ".go", ".rs", ".java"):
                    source += 1
                elif ext == ".md":
                    doc += 1
                elif "test" in f.name.lower():
                    test += 1

    return RepoScan(
        root=str(root),
        layers=layers,
        total_files=total,
        source_files=source,
        doc_files=doc,
        test_files=test,
    )


def _layer_purpose(layer: str) -> str:
    purposes = {
        "L0": "Governed seed kernel — protected runtime",
        "L1": "External evolution / Controller governance",
        "L2": "Specialization profile/spec layer",
    }
    return purposes.get(layer, "")
