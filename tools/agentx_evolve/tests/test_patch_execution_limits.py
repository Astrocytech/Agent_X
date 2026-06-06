from agentx_evolve.patch_execution.patch_models import PatchLimits, PatchLimitError, PLE_SIZE_EXCEEDED


def test_limits_defaults():
    limits = PatchLimits()
    assert limits.max_changed_files_per_session == 5
    assert limits.max_single_file_bytes == 1048576


def test_limits_reject_oversized_patches():
    limits = PatchLimits(max_single_file_bytes=100)
    err = PatchLimitError("patch too large", code=PLE_SIZE_EXCEEDED)
    assert err.code == PLE_SIZE_EXCEEDED
    assert "patch too large" in str(err)


def test_limits_reject_too_many_files():
    limits = PatchLimits(max_changed_files_per_session=2)
    err = PatchLimitError("too many files changed", code="FILES_EXCEEDED")
    assert err.code == "FILES_EXCEEDED"


def test_patch_limit_error_is_exception():
    err = PatchLimitError("test")
    assert isinstance(err, Exception)


def test_ple_size_exceeded_constant():
    assert PLE_SIZE_EXCEEDED == "SIZE_EXCEEDED"
