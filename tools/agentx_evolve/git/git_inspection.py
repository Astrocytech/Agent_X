import warnings
from agentx_evolve.git.git_status import git_status
from agentx_evolve.git.git_diff import git_diff, git_diff_name_only, git_diff_stat
warnings.warn(
    "agentx_evolve.git.git_inspection is deprecated; "
    "use agentx_evolve.git.git_status or agentx_evolve.git.git_diff instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["git_status", "git_diff", "git_diff_name_only", "git_diff_stat"]
