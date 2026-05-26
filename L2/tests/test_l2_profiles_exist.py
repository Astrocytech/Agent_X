"""L2 structure tests."""

import os


L2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_l2_profiles_dir_exists():
    assert os.path.isdir(os.path.join(L2_DIR, "profiles"))


def test_l2_has_profile_files():
    profiles = os.listdir(os.path.join(L2_DIR, "profiles"))
    assert any(f.endswith(".yaml") for f in profiles)


def test_l2_blueprints_exist():
    assert os.path.isdir(os.path.join(L2_DIR, "blueprints"))


def test_l2_extension_specs_exist():
    assert os.path.isdir(os.path.join(L2_DIR, "extension_specs"))


def test_l2_evaluation_specs_exist():
    assert os.path.isdir(os.path.join(L2_DIR, "evaluation_specs"))


def test_l2_integration_specs_exist():
    assert os.path.isdir(os.path.join(L2_DIR, "integration_specs"))
