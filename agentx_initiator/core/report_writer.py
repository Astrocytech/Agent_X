from pathlib import Path
from jinja2 import Environment, FileSystemLoader
from agentx_initiator.core.paths import repo_root, report_file


def get_template_env():
    template_dir = repo_root() / "agentx_initiator" / "templates"
    return Environment(loader=FileSystemLoader(str(template_dir)))


def render_report(template_name: str, context: dict) -> str:
    env = get_template_env()
    template = env.get_template(template_name)
    return template.render(**context)


def write_report(name: str, content: str):
    path = report_file(name)
    path.write_text(content)
    return path
