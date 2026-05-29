"""L1 structure tests."""

import os


L1_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_l1_controller_exists():
    assert os.path.isdir(os.path.join(L1_DIR, "controller"))


def test_l1_patch_planner_exists():
    assert os.path.isdir(os.path.join(L1_DIR, "patch_planner"))


def test_l1_proof_runner_exists():
    assert os.path.isdir(os.path.join(L1_DIR, "proof_runner"))


def test_l1_workflows_exist():
    workflows = os.listdir(os.path.join(L1_DIR, "workflows"))
    assert "evolve_once.yaml" in workflows
    assert "verify_only.yaml" in workflows


def test_l1_prompts_exist():
    prompts = os.listdir(os.path.join(L1_DIR, "prompts"))
    assert any(f.endswith(".md") for f in prompts)
