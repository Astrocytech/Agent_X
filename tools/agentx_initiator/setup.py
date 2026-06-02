from setuptools import setup
from pathlib import Path

root = Path(__file__).parent
packages = []
for p in root.rglob("__init__.py"):
    rel = p.parent.relative_to(root)
    if str(rel) == ".":
        packages.append("agentx_initiator")
    else:
        packages.append("agentx_initiator." + str(rel).replace("/", "."))

setup(
    packages=packages,
    package_dir={"agentx_initiator": "."},
    include_package_data=True,
    package_data={
        "agentx_initiator.templates": ["*.j2"],
        "agentx_initiator.schemas": ["*.json"],
    },
)
