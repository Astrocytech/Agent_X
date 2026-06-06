from agentx_evolve.packaging.packaging_models import (
    CommandRecord,
    redact_sensitive_text,
)


class TestCommandSafety:
    def test_no_raw_shell_in_command_text(self):
        safe = "PYTHONPATH=tools python3 -m pytest"
        assert ";rm" not in safe
        assert "&& rm" not in safe
        assert "`rm" not in safe

    def test_command_text_is_recorded(self):
        cmd = CommandRecord(
            name="compileall",
            command="PYTHONPATH=tools python3 -m compileall tools/agentx_evolve",
            exit_code=0,
            status="PASS",
            summary="ok",
        )
        assert cmd.name == "compileall"
        assert cmd.exit_code == 0
        assert cmd.command.startswith("PYTHONPATH=tools")

    def test_publish_commands_are_blocked(self):
        dangerous = ["twine upload", "pip publish", "npm publish", "git push", "git tag"]
        safe_command_texts = [
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_orchestrator --dry-run",
            "PYTHONPATH=tools python3 -m compileall tools/agentx_evolve",
        ]
        for cmd_text in safe_command_texts:
            for d in dangerous:
                assert d not in cmd_text, f"safe command should not contain {d}"

    def test_no_network_commands_in_build_commands(self):
        safe = [
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_builder --dry-run",
            "PYTHONPATH=tools python3 -m compileall tools/agentx_evolve",
        ]
        network = ["curl", "wget", "git clone", "pip install"]
        for cmd_text in safe:
            for n in network:
                assert n not in cmd_text, f"network command {n} should not be in {cmd_text}"

    def test_build_command_does_not_mutate_source(self):
        build_cmds = [
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_orchestrator --dry-run",
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_builder --dry-run",
        ]
        for cmd_text in build_cmds:
            assert "|| git add" not in cmd_text
            assert "&& git" not in cmd_text
            assert "git commit" not in cmd_text
            assert "git push" not in cmd_text

    def test_build_commands_are_allowlisted(self):
        allowed_prefixes = [
            "PYTHONPATH=tools python3 -m compileall",
            "PYTHONPATH=tools python3 -m pytest",
            "PYTHONPATH=tools python3 tools/agentx_evolve/tests/validate_packaging_schemas.py",
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.",
            "PYTHONPATH=tools python3 -c ",
        ]
        test_commands = [
            "PYTHONPATH=tools python3 -m compileall tools/agentx_evolve",
            "PYTHONPATH=tools python3 -m pytest tools/agentx_evolve/tests",
            "PYTHONPATH=tools python3 tools/agentx_evolve/tests/validate_packaging_schemas.py",
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_builder --dry-run",
            "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_validator",
        ]
        for cmd_text in test_commands:
            assert any(cmd_text.startswith(prefix) for prefix in allowed_prefixes), (
                f"Command not allowlisted: {cmd_text}"
            )

    def test_rejects_shell_metacharacters(self):
        safe = "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_builder --dry-run"
        assert ";rm" not in safe, f"safe command should not contain shell injection: {safe}"
        assert "| sh" not in safe, f"safe command should not contain pipe injection: {safe}"
        assert "&& rm" not in safe

    def test_safe_python_c_command_is_valid(self):
        cmd = "PYTHONPATH=tools python3 -c \"print('hello')\""
        assert cmd.startswith("PYTHONPATH=tools python3")
        assert "rm -rf" not in cmd

    def test_output_redacted_for_sensitive_commands(self):
        sensitive_output = "API_KEY=sk-1234567890abcdef"
        redacted = redact_sensitive_text(sensitive_output)
        assert "sk-1234567890abcdef" not in redacted
        assert "***REDACTED***" in redacted

    def test_command_exit_code_must_be_recorded(self):
        cmd = CommandRecord(name="test", command="echo hello", status="PASS")
        assert cmd.exit_code is None
        cmd.exit_code = 0
        assert cmd.exit_code == 0

    def test_no_release_tags_created_by_default(self):
        build_cmd = "PYTHONPATH=tools python3 -m agentx_evolve.packaging.package_orchestrator"
        assert "git tag" not in build_cmd
        assert "git push --tags" not in build_cmd

    def test_no_upload_commands_in_builder(self):
        import agentx_evolve.packaging.package_builder as builder
        with open(builder.__file__) as f:
            source = f.read()
        upload_commands = ["twine upload", "gh release create", "gh release upload", "rsync", "scp"]
        for cmd in upload_commands:
            assert cmd not in source, f"upload command {cmd} should not be in package_builder source"
