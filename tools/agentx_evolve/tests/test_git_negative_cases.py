from agentx_evolve.git.git_operations import GitOperationError, GOE_FILE_NOT_FOUND, GOE_PERMISSION_DENIED


def test_error_types_differentiate():
    err1 = GitOperationError("file missing", code=GOE_FILE_NOT_FOUND)
    err2 = GitOperationError("permission denied", code=GOE_PERMISSION_DENIED)
    assert err1.code == GOE_FILE_NOT_FOUND
    assert err2.code == GOE_PERMISSION_DENIED
    assert err1.code != err2.code


def test_error_wraps_original_exception():
    original = ValueError("underlying issue")
    err = GitOperationError("wrapped", code=GOE_FILE_NOT_FOUND, original=original)
    assert err.original is original
    assert isinstance(err.original, ValueError)


def test_error_defaults():
    err = GitOperationError()
    assert err.code == ""
    assert err.original is None


def test_error_is_exception():
    err = GitOperationError("test")
    assert isinstance(err, Exception)


def test_goe_constants_have_correct_values():
    assert GOE_FILE_NOT_FOUND == "FILE_NOT_FOUND"
    assert GOE_PERMISSION_DENIED == "PERMISSION_DENIED"
