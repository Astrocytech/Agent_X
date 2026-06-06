import pytest
import tempfile
from pathlib import Path

from agentx_evolve.docs_sync.doc_deviations import (
    create_docs_sync_deviation,
    validate_docs_sync_deviation,
    write_docs_sync_deviation_register,
)


class TestDeviations:
    def test_deviation_register_written(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            deviations = [
                create_docs_sync_deviation(
                    area="links",
                    description="external links not checked",
                    reason="network not available",
                    accepted_status="DEFERRED_SAFELY",
                    reviewer_decision="acceptable",
                ),
            ]
            result = write_docs_sync_deviation_register(root, deviations)
            assert result["status"] == "written"
            path = root / ".agentx-init/docs_sync/documentation_sync_deviation_register.json"
            assert path.exists()

    def test_create_deviation_valid(self):
        dev = create_docs_sync_deviation(
            area="testing",
            description="some tests deferred",
            reason="not implemented yet",
            accepted_status="DEFERRED_SAFELY",
            reviewer_decision="approved",
        )
        assert dev["area"] == "testing"
        assert dev["accepted_status"] == "DEFERRED_SAFELY"

    def test_create_deviation_invalid_status(self):
        dev = create_docs_sync_deviation(
            area="test",
            description="test",
            reason="test",
            accepted_status="INVALID",
        )
        assert dev["status"] == "INVALID"

    def test_validate_deviation_clean(self):
        dev = create_docs_sync_deviation(
            area="test",
            description="clean deviation",
            reason="valid reason",
            accepted_status="NON_BLOCKING_FOLLOWUP",
            reviewer_decision="ok",
        )
        valid, errors = validate_docs_sync_deviation(dev)
        assert valid is True
