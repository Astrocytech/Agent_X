import warnings
from agentx_evolve.git.git_evidence import (
    write_git_completion_record, write_git_evidence_manifest, write_git_review_report,
)
warnings.warn(
    "agentx_evolve.git.git_completion is deprecated; "
    "use agentx_evolve.git.git_evidence instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["write_git_completion_record", "write_git_evidence_manifest", "write_git_review_report"]
