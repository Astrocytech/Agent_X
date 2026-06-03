from pathlib import Path
from agentx_evolve.docs_sync.validate_docs_sync_schemas import (
    SCHEMA_FILES, SCHEMA_DIR, validate_all_docs_sync_schemas,
    main,
)


class TestSchemaConstants:
    def test_schema_files_list(self):
        assert len(SCHEMA_FILES) > 0
        assert all(f.endswith(".json") for f in SCHEMA_FILES)
        assert "documentation_record.schema.json" in SCHEMA_FILES

    def test_schema_dir(self):
        assert SCHEMA_DIR.name == "schemas"
        assert SCHEMA_DIR.exists()


class TestValidateAllDocsSyncSchemas:
    def test_validates_successfully(self):
        result = validate_all_docs_sync_schemas()
        assert result == 0

    def test_missing_schema_reports_error(self, tmp_path):
        empty_dir = tmp_path / "schemas"
        empty_dir.mkdir()
        original_dir = SCHEMA_DIR
        try:
            import agentx_evolve.docs_sync.validate_docs_sync_schemas as m
            m.SCHEMA_DIR = empty_dir
            result = m.validate_all_docs_sync_schemas()
            assert result == 1
        finally:
            m.SCHEMA_DIR = original_dir

    def test_main(self):
        result = main()
        assert result == 0
