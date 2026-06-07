import pytest

from agentx_evolve.runtime.plan_parser import StructuredPlanParser, PlanParseError


class TestStructuredPlanParser:
    def setup_method(self):
        self.parser = StructuredPlanParser()

    def test_valid_plan(self):
        plan = {
            "schema_version": "agentx.structured_plan.v1",
            "summary": "add logging to config resolver",
            "actions": [
                {
                    "type": "patch",
                    "description": "add debug logging",
                    "target": "runtime/config.py",
                    "safety_notes": ["no external calls"],
                }
            ],
            "patches": [
                {
                    "format": "unified_diff",
                    "content": "diff --git a/foo b/bar\n--- a/foo\n+++ b/bar\n@@ -1 +1 @@\n-old\n+new\n",
                }
            ],
            "validation_commands": [
                "python -m compileall tools/agentx_evolve",
            ],
        }
        result = self.parser.parse(plan)
        assert result["schema_version"] == "agentx.structured_plan.v1"

    def test_valid_plan_no_patches(self):
        plan = {
            "schema_version": "agentx.structured_plan.v1",
            "summary": "report only",
            "actions": [{"type": "report", "description": "generate report", "target": ""}],
            "patches": [],
            "validation_commands": [],
        }
        result = self.parser.parse(plan)
        assert result["summary"] == "report only"

    def test_missing_schema_version(self):
        with pytest.raises(PlanParseError, match="missing schema_version"):
            self.parser.parse({"summary": "test", "actions": [], "patches": [], "validation_commands": []})

    def test_wrong_schema_version(self):
        with pytest.raises(PlanParseError, match="unknown schema_version"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v2",
                "summary": "test", "actions": [], "patches": [], "validation_commands": [],
            })

    def test_missing_summary(self):
        with pytest.raises(PlanParseError, match="missing or invalid summary"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "actions": [], "patches": [], "validation_commands": [],
            })

    def test_unknown_action_type(self):
        with pytest.raises(PlanParseError, match="unknown type"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "delete", "description": "bad"}],
                "patches": [], "validation_commands": [],
            })

    def test_action_missing_description(self):
        with pytest.raises(PlanParseError, match="missing or invalid description"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "noop", "description": ""}],
                "patches": [], "validation_commands": [],
            })

    def test_absolute_path_target(self):
        with pytest.raises(PlanParseError, match="absolute path"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "patch", "description": "bad", "target": "/etc/passwd"}],
                "patches": [], "validation_commands": [],
            })

    def test_path_traversal_target(self):
        with pytest.raises(PlanParseError, match="path traversal"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "patch", "description": "bad", "target": "../../etc/passwd"}],
                "patches": [], "validation_commands": [],
            })

    def test_patch_unknown_format(self):
        with pytest.raises(PlanParseError, match="unknown format"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "patch", "description": "test", "target": "foo.py"}],
                "patches": [{"format": "binary", "content": "data"}],
                "validation_commands": [],
            })

    def test_patch_empty_content(self):
        with pytest.raises(PlanParseError, match="missing or empty content"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "patch", "description": "test", "target": "foo.py"}],
                "patches": [{"format": "unified_diff", "content": ""}],
                "validation_commands": [],
            })

    def test_patch_not_unified_diff(self):
        with pytest.raises(PlanParseError, match="does not look like unified diff"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "patch", "description": "test", "target": "foo.py"}],
                "patches": [{"format": "unified_diff", "content": "just some text"}],
                "validation_commands": [],
            })

    def test_parse_from_json_string(self):
        plan_str = """{
            "schema_version": "agentx.structured_plan.v1",
            "summary": "from string",
            "actions": [{"type": "noop", "description": "test", "target": ""}],
            "patches": [],
            "validation_commands": []
        }"""
        result = self.parser.parse(plan_str)
        assert result["summary"] == "from string"

    def test_malformed_json_string(self):
        with pytest.raises(PlanParseError, match="malformed JSON"):
            self.parser.parse("{invalid json")

    def test_blocked_command(self):
        with pytest.raises(PlanParseError, match="blocked command"):
            self.parser.parse({
                "schema_version": "agentx.structured_plan.v1",
                "summary": "test",
                "actions": [{"type": "noop", "description": "bad", "target": ""}],
                "patches": [],
                "validation_commands": ["rm -rf /"],
            })
