import warnings
from agentx_evolve.git.git_stage import git_stage
from agentx_evolve.git.git_commit import git_commit
from agentx_evolve.git.git_branch import git_branch
from agentx_evolve.git.git_push import git_push
from agentx_evolve.git.git_revert import git_revert
warnings.warn(
    "agentx_evolve.git.git_mutation is deprecated; "
    "use agentx_evolve.git.git_stage, agentx_evolve.git.git_commit, "
    "agentx_evolve.git.git_branch, agentx_evolve.git.git_push, "
    "or agentx_evolve.git.git_revert instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = ["git_stage", "git_commit", "git_branch", "git_push", "git_revert"]
