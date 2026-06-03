from agentx_evolve.context.validation_error_summarizer import (
    ValidationErrorEntry, ValidationErrorSummary, summarize_test_output,
)


class TestValidationErrorEntry:
    def test_defaults(self):
        entry = ValidationErrorEntry()
        assert entry.test_name == ""
        assert entry.error_message == ""
        assert entry.file == ""
        assert entry.line == 0

    def test_with_values(self):
        entry = ValidationErrorEntry(
            test_name="test_foo",
            error_message="AssertionError",
            file="test_file.py",
            line=42,
        )
        assert entry.test_name == "test_foo"
        assert entry.line == 42

    def test_to_dict(self):
        entry = ValidationErrorEntry(test_name="t1", error_message="err")
        d = entry.to_dict()
        assert d["test_name"] == "t1"


class TestValidationErrorSummary:
    def test_defaults(self):
        summary = ValidationErrorSummary()
        assert summary.total_errors == 0
        assert summary.total_failures == 0
        assert summary.entries == []
        assert summary.summary_text == ""

    def test_to_dict(self):
        summary = ValidationErrorSummary(
            total_errors=2, total_failures=3,
            entries=[ValidationErrorEntry(error_message="err1")],
            summary_text="2 failures",
        )
        d = summary.to_dict()
        assert d["total_errors"] == 2
        assert len(d["entries"]) == 1
        assert d["summary_text"] == "2 failures"


class TestSummarizeTestOutput:
    def test_empty_output(self):
        summary = summarize_test_output("")
        assert summary.total_errors == 0
        assert summary.total_failures == 0
        assert "No test output" in summary.summary_text

    def test_no_errors(self):
        summary = summarize_test_output("All tests passed!")
        assert summary.total_errors == 0
        assert summary.total_failures == 0

    def test_with_failures_and_errors(self):
        output = "test_foo FAILED\n"
        output += "test_bar ERROR\n"
        output += "test_baz FAILED\n"
        summary = summarize_test_output(output)
        assert summary.total_failures == 2
        assert summary.total_errors == 1
        assert len(summary.entries) == 3

    def test_truncates_more_than_20(self):
        lines = "\n".join([f"test_{i} ERROR" for i in range(25)])
        summary = summarize_test_output(lines)
        assert len(summary.entries) == 20
        assert any("Truncated" in w for w in summary.warnings)

    def test_summary_text_format(self):
        summary = summarize_test_output("test_a FAILED\ntest_b ERROR")
        assert "failures" in summary.summary_text
        assert "errors" in summary.summary_text
        assert "2 entries" in summary.summary_text
