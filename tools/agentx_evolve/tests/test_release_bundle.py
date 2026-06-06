from pathlib import Path

import pytest

from agentx_evolve.packaging.release_bundle import create_release_bundle
from agentx_evolve.packaging.packaging_models import (
    ArtifactHashManifest, ArtifactHashRecord, PackageProvenance,
)


class TestReleaseBundle:
    def test_bundle_contains_package(self, tmp_path: Path):
        pkg = tmp_path / "dist" / "pkg.tar.gz"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("fake package")
        evidence = tmp_path / "evidence" / "report.json"
        evidence.parent.mkdir(parents=True)
        evidence.write_text("{}")
        hash_manifest = ArtifactHashManifest(artifacts=[
            ArtifactHashRecord(artifact_path=str(pkg), sha256="a" * 64, size_bytes=12, artifact_kind="tar.gz"),
        ])
        provenance = PackageProvenance(package_name="testpkg", package_version="1.0")
        output_root = tmp_path / "bundles"
        bundle = create_release_bundle(pkg, [evidence], hash_manifest, provenance, output_root)
        assert bundle.bundle_artifact is not None
        bundle_dir = Path(bundle.bundle_artifact)
        assert bundle_dir.exists()
        artifacts_dir = bundle_dir / "artifacts"
        assert artifacts_dir.exists()
        assert (artifacts_dir / pkg.name).exists()

    def test_bundle_contains_evidence(self, tmp_path: Path):
        pkg = tmp_path / "dist" / "pkg.tar.gz"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("fake")
        ev1 = tmp_path / "evidence" / "report.json"
        ev1.parent.mkdir(parents=True)
        ev1.write_text('{"key": "val"}')
        hash_manifest = ArtifactHashManifest()
        provenance = PackageProvenance(package_name="p", package_version="1")
        output_root = tmp_path / "bundles"
        bundle = create_release_bundle(pkg, [ev1], hash_manifest, provenance, output_root)
        bundle_dir = Path(bundle.bundle_artifact)
        evidence_dir = bundle_dir / "evidence"
        assert evidence_dir.exists()
        assert (evidence_dir / ev1.name).exists()

    def test_bundle_manifest_written(self, tmp_path: Path):
        pkg = tmp_path / "dist" / "pkg.tar.gz"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("fake")
        hash_manifest = ArtifactHashManifest()
        provenance = PackageProvenance(package_name="p", package_version="1")
        output_root = tmp_path / "bundles"
        bundle = create_release_bundle(pkg, [], hash_manifest, provenance, output_root)
        assert bundle.bundle_manifest_id.startswith("bundle_")
        assert bundle.bundle_name == "release_bundle_p_1"
        bundle_dir = Path(bundle.bundle_artifact)
        manifest_path = bundle_dir / "release_bundle_manifest.json"
        assert manifest_path.exists()

    def test_bundle_does_not_publish(self, tmp_path: Path):
        pkg = tmp_path / "dist" / "pkg.tar.gz"
        pkg.parent.mkdir(parents=True)
        pkg.write_text("fake")
        hash_manifest = ArtifactHashManifest()
        provenance = PackageProvenance(package_name="p", package_version="1")
        output_root = tmp_path / "bundles"
        bundle = create_release_bundle(pkg, [], hash_manifest, provenance, output_root)
        assert bundle.promotion_status == "NOT_PROMOTED"
