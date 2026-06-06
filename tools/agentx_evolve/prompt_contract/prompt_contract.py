import warnings
warnings.warn(
    "prompt_contract is deprecated; use agentx_evolve.prompts instead",
    DeprecationWarning,
    stacklevel=2,
)

# Legacy constants (backward-compatible)
PC_SCHEMA_VERSION = "1.0"
PC_ACTIVE = "ACTIVE"
PC_DEPRECATED = "DEPRECATED"
PC_RETIRED = "RETIRED"
ALL_PROMPT_CONTRACT_STATUSES = [PC_ACTIVE, PC_DEPRECATED, PC_RETIRED]

# Canonical models (with legacy aliases where names differ)
from agentx_evolve.prompts.prompt_models import (
    PromptContract as PromptContract,
    PromptVersion as PromptVersionRecord,
    PromptRegistry as PromptContractRegistry,
    PromptRegistrySnapshot as PromptRegistrySnapshot,
    PromptInputContract as PromptInputContract,
    PromptOutputContract as PromptOutputContract,
    PromptSafetyRule as PromptSafetyRule,
    PromptProvenance as PromptProvenance,
    PromptDiffRecord as PromptDiff,
    PromptMigrationRecord as PromptMigration,
    PromptRuntimeBinding as PromptRuntimeBinding,
    PromptWorkerPayload as PromptWorkerPayload,
    PromptPermissionDecision as PromptPermissionDecision,
    PromptAuditEvent as PromptAuditEvent,
)

# Canonical submodule functions
from agentx_evolve.prompts.prompt_registry import (
    register_prompt_contract,
    get_prompt_contract,
)
from agentx_evolve.prompts.prompt_validator import validate_prompt_contract
from agentx_evolve.prompts.prompt_versioning import create_prompt_version
from agentx_evolve.prompts.prompt_compatibility import check_prompt_compatibility
from agentx_evolve.prompts.prompt_diff import create_prompt_diff
from agentx_evolve.prompts.prompt_migration import (
    create_prompt_migration_record,
    mark_prompt_migration_complete,
)
from agentx_evolve.prompts.prompt_runtime_binding import (
    bind_prompt_for_runtime,
    resolve_prompt_body,
)
from agentx_evolve.prompts.prompt_safety import check_prompt_body_safety
from agentx_evolve.prompts.prompt_provenance import create_prompt_provenance
from agentx_evolve.prompts.prompt_audit_logger import append_prompt_audit_event
