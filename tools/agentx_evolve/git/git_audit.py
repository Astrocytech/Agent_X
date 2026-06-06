import warnings
from agentx_evolve.git.git_evidence import (
    append_git_operation, append_git_result, append_git_blocked,
    append_git_mutation_request, append_git_commit_evidence,
    write_latest_artifact, write_latest_operation, write_latest_result,
    write_git_evidence_manifest, write_git_review_report, write_git_completion_record,
)
warnings.warn(
    "agentx_evolve.git.git_audit is deprecated; "
    "use agentx_evolve.git.git_evidence instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "append_git_operation", "append_git_result", "append_git_blocked",
    "append_git_mutation_request", "append_git_commit_evidence",
    "write_latest_artifact", "write_latest_operation", "write_latest_result",
    "write_git_evidence_manifest", "write_git_review_report", "write_git_completion_record",
]
