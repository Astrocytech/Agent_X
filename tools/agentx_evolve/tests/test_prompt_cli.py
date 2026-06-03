import pytest
from agentx_evolve.prompts.prompt_cli import build_parser, main


class TestBuildParser:
    def test_parser_created(self):
        parser = build_parser()
        assert parser.prog == "prompt-cli"

    def test_parse_validate(self):
        parser = build_parser()
        args = parser.parse_args(["--validate", "prompt.yaml"])
        assert args.validate == "prompt.yaml"

    def test_parse_list(self):
        parser = build_parser()
        args = parser.parse_args(["--list"])
        assert args.list is True


class TestMain:
    def test_main_no_args(self):
        rc = main([])
        assert rc == 0

    def test_main_validate(self):
        rc = main(["--validate", "x.yaml"])
        assert rc == 1

    def test_main_bind(self):
        rc = main(["--bind", "contract"])
        assert rc == 1
