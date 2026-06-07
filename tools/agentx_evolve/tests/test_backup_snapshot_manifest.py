import pytest
# snapshot_manifest module has no public classes/functions, test imports only
import agentx_evolve.backup.snapshot_manifest as sm


class TestBackupSnapshotManifest:
    def test_module_importable(self):
        assert sm is not None
