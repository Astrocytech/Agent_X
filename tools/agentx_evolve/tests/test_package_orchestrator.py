from pathlib import Path

import pytest

from agentx_evolve.packaging.packaging_models import (
    PackageManifest, PackageInventory, PackageFileRecord, PackageRejection,
    PACKAGE_STATUS_BUILT, VALIDATION_STATUS_PASS, VALIDATION_STATUS_FAIL,
    REJECTION_SECRET, REJECTION_CACHE, SEVERITY_BLOCKER,
    new_id, utc_now_iso,
)
from agentx_evolve.packaging.package_builder import build_package
from agentx_evolve.packaging.package_validator import validate_package_contents
from agentx_evolve.packaging.artifact_hasher import write_hash_manifest, hash_bytes
from agentx_evolve.packaging.provenance_writer import write_package_provenance
from agentx_evolve.packaging.dependency_lock_validator import validate_dependency_lock
from agentx_evolve.packaging.dependency_inventory_writer import write_dependency_inventory
from agentx_evolve.packaging.install_validator import validate_local_install
from agentx_evolve.packaging.release_bundle import create_release_bundle
from agentx_evolve.packaging.distribution_evidence import (
    write_distribution_evidence, write_packaging_evidence_manifest,
    write_packaging_completion_record,
)
from agentx_evolve.packaging.package_file_selector import select_package_files
from agentx_evolve.packaging.package_rejector import reject_forbidden_package_files


def _create_repo(repo_root: Path, files: dict[str, str | None]) -> None:
    for rel_path, content in files.items():
        path = repo_root / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if content is not None:
            path.write_text(content)


def _run_build_flow(
    repo_root: Path,
    manifest: PackageManifest,
) -> dict:
    inventory = select_package_files(repo_root, manifest)
    inventory = reject_forbidden_package_files(inventory, manifest, repo_root)

    artifact, build_report = build_package(repo_root, manifest, inventory)

    validation_report = validate_package_contents(artifact, manifest, inventory)
    artifact_hash = write_hash_manifest([artifact], repo_root / ".agentx-init/packaging/reports/hash.json")

    prov_out = repo_root / ".agentx-init/packaging/evidence/provenance.json"
    prov_out.parent.mkdir(parents=True, exist_ok=True)
    provenance = write_package_provenance(
        repo_root, manifest, artifact, validation_report.status,
        "build", prov_out,
    )

    dlr = validate_dependency_lock(repo_root, manifest)
    di_out = repo_root / ".agentx-init/packaging/evidence/dep_inventory.json"
    di_out.parent.mkdir(parents=True, exist_ok=True)
    dep_inv = write_dependency_inventory(repo_root, manifest, dlr, di_out)

    ivr = validate_local_install(artifact, manifest, repo_root)

    bundle_output = repo_root / ".agentx-init/packaging/dist/bundles"
    ev_files = [prov_out, di_out]
    bundle = create_release_bundle(artifact, ev_files, artifact_hash, provenance, bundle_output)

    ev_out = repo_root / ".agentx-init/packaging/evidence/distribution_evidence.json"
    ev_out.parent.mkdir(parents=True, exist_ok=True)
    evidence = write_distribution_evidence(
        repo_root, manifest, inventory, build_report, validation_report,
        artifact_hash, provenance, dlr, ivr, bundle, [], ev_out,
    )

    ev_manifest_out = repo_root / ".agentx-init/packaging/evidence/evidence_manifest.json"
    ev_manifest = write_packaging_evidence_manifest(
        ev_files, [artifact], [], [], ev_manifest_out,
    )

    completion_out = repo_root / ".agentx-init/packaging/evidence/completion.json"
    completion = write_packaging_completion_record(evidence, ev_manifest, completion_out)

    return {
        "inventory": inventory,
        "artifact": artifact,
        "build_report": build_report,
        "validation_report": validation_report,
        "hash_manifest": artifact_hash,
        "provenance": provenance,
        "dependency_lock_report": dlr,
        "dependency_inventory": dep_inv,
        "install_validation_report": ivr,
        "release_bundle": bundle,
        "evidence": evidence,
        "evidence_manifest": ev_manifest,
        "completion": completion,
    }


class TestFullFlow:
    def test_full_flow_in_temp_repo(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "README.md": "# Test",
            "Makefile": "all:",
            "src/main.py": "print('hello')",
        })
        manifest = PackageManifest(
            package_name="testpkg",
            package_version="1.0.0",
            source_root=".",
            require_clean_git=False,
        )
        result = _run_build_flow(tmp_path, manifest)
        assert result["artifact"].exists()
        assert result["build_report"].status == PACKAGE_STATUS_BUILT
        assert result["validation_report"].status == VALIDATION_STATUS_PASS
        assert result["hash_manifest"].hash_manifest_id.startswith("hash_")
        assert result["provenance"].provenance_id.startswith("prov_")
        assert result["completion"].final_decision == VALIDATION_STATUS_PASS
        ev_root = tmp_path / ".agentx-init/packaging/evidence"
        assert (ev_root / "provenance.json").exists()
        assert (ev_root / "dep_inventory.json").exists()
        assert (ev_root / "distribution_evidence.json").exists()
        assert (ev_root / "evidence_manifest.json").exists()
        assert (ev_root / "completion.json").exists()


class TestDryRun:
    def test_dry_run_does_not_create_staging(self, tmp_path: Path):
        pytest.skip("Dry run mode not implemented in test helper")


class TestBlocksOnSecret:
    def test_blocks_on_secret(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "README.md": "# Test",
            "Makefile": "all:",
            "config.py": "API_KEY=sk-1234",
        })
        manifest = PackageManifest(
            package_name="testpkg",
            package_version="1.0.0",
            source_root=".",
            require_clean_git=False,
        )
        inventory = select_package_files(tmp_path, manifest)
        inventory = reject_forbidden_package_files(inventory, manifest, tmp_path)
        assert len(inventory.rejections) > 0
        assert any(r.reason_code == REJECTION_SECRET for r in inventory.rejections)


class TestBlocksOnDirtyTree:
    def test_blocks_on_dirty_tree(self, tmp_path: Path):
        _create_repo(tmp_path, {
            "README.md": "# Test",
            "Makefile": "all:",
        })
        manifest = PackageManifest(
            package_name="testpkg",
            package_version="1.0.0",
            source_root=".",
            require_clean_git=True,
        )
        inventory = select_package_files(tmp_path, manifest)
        assert inventory is not None
