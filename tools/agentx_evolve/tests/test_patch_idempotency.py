from agentx_evolve.patch_execution.patch_applier import apply_patch, is_already_applied


def test_applying_same_patch_twice_is_idempotent():
    patch = "--- a/file.py\n+++ b/file.py\n@@ -1 +1 @@\n-old\n+new"
    result1 = apply_patch(patch, "file.py", "/tmp/repo")
    result2 = apply_patch(patch, "file.py", "/tmp/repo")
    assert result1.status == result2.status


def test_detects_already_applied_patch():
    patch = "diff --git a/test.py b/test.py"
    assert is_already_applied(patch, "test.py", "/tmp/repo") is False
    apply_patch(patch, "test.py", "/tmp/repo")
    assert is_already_applied(patch, "test.py", "/tmp/repo") is True


def test_apply_patch_returns_result():
    patch = "simple patch content"
    result = apply_patch(patch, "target.py", "/tmp/repo")
    assert result.changed_paths == ["target.py"]


def test_different_patches_not_confused():
    patch_a = "patch A content"
    patch_b = "patch B content"
    apply_patch(patch_a, "a.py", "/tmp/repo")
    assert is_already_applied(patch_a, "a.py", "/tmp/repo") is True
    assert is_already_applied(patch_b, "b.py", "/tmp/repo") is False
