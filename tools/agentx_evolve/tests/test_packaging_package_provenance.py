import pytest
from agentx_evolve.packaging.package_provenance import PackageProvenance


class TestPackageProvenance:
    def test_defaults(self):
        p = PackageProvenance()
        assert p.source_repo == ""
        assert p.build_command == ""
        assert p.builder == ""

    def test_to_dict(self):
        p = PackageProvenance(
            source_repo="https://github.com/org/repo",
            build_command="make build",
            builder="ci-bot",
            build_id="b-001",
        )
        d = p.to_dict()
        assert d["source_repo"] == "https://github.com/org/repo"
        assert d["build_command"] == "make build"
        assert d["builder"] == "ci-bot"
        assert d["build_id"] == "b-001"
