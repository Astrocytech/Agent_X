from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from agentx_initiator.core.path_registry import _detect_repo_root, get_path


def get_template_env():
    template_dir = Path(__file__).resolve().parent.parent / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)))


def render_report(template_name: str, context: dict) -> str:
    env = get_template_env()
    template = env.get_template(template_name)
    return template.render(**context)


def write_report(name: str, content: str) -> Path:
    path = get_path("reports_dir") / name
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def render_architecture_report(arch_result: dict) -> str:
    return render_report("architecture_report.md.j2", arch_result)


def render_governance_report(gov_result: dict) -> str:
    return render_report("governance_report.md.j2", gov_result)


def render_risk_assessment(risk_result: dict) -> str:
    return render_report("risk_assessment.md.j2", risk_result)


def render_memory_snapshot(snapshot_result: dict) -> str:
    return render_report("memory_snapshot.md.j2", snapshot_result)


def render_memory_index(index_result: dict) -> str:
    return render_report("memory_index.md.j2", index_result)


def render_memory_manifest(manifest_result: dict) -> str:
    return render_report("memory_manifest.md.j2", manifest_result)


def render_evolution_manifest(manifest_result: dict) -> str:
    return render_report("evolution_manifest.md.j2", manifest_result)


def render_patch_manifest(manifest_result: dict) -> str:
    return render_report("patch_manifest.md.j2", manifest_result)
