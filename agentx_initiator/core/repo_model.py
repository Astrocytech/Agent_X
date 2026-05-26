from pydantic import BaseModel
from pathlib import Path


class LayerEntry(BaseModel):
    layer: str
    path: Path
    purpose: str = ""
    file_count: int = 0
    has_readme: bool = False


class FileEntry(BaseModel):
    path: Path
    relative_path: str
    size_bytes: int
    extension: str


class RepoScan(BaseModel):
    root: str
    layers: list[LayerEntry]
    total_files: int
    source_files: int
    doc_files: int
    test_files: int


class ArchitectureReport(BaseModel):
    layers: list[LayerEntry]
    layer_count: int
    valid_layer_structure: bool
    l0_independent: bool
    l1_separated: bool
    l2_contains_active_runtime: bool
    risks: list[dict] = []
