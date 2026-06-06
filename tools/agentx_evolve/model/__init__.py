"""
[DEPRECATED] agentx_evolve.model — legacy v1 model adapter package.

This package is the v1 proof-of-concept model system. It has been superseded
by the v2 production-grade system at ``agentx_evolve.models`` (schema-versioned
dataclasses, policy engine, proper provider adapters, call logging, retry).

New code should import from ``agentx_evolve.models`` instead.
This package is preserved for existing consumers (e.g. ``PromptRunner``,
``ModelRegistry``, ``JsonOutputValidator``) and will be removed in a future
release after all consumers are migrated to the v2 API.
"""
import warnings
warnings.warn(
    "agentx_evolve.model is deprecated; use agentx_evolve.models instead",
    DeprecationWarning, stacklevel=2,
)

from agentx_evolve.model.model_models import (
    ModelProfile, PromptRequest, ModelResponse, ModelProviderConfig,
    MP_SMALL_FAST, MP_SMALL_CODER, MP_MEDIUM_CODER, MP_HOSTED_FALLBACK,
    MD_SUCCESS, MD_FAILED, MD_INVALID_OUTPUT, MD_INSUFFICIENT_CONTEXT, MD_TIMEOUT, MD_RATE_LIMITED,
    TASK_IMPLEMENT_PATCH, TASK_FIX_VALIDATION, TASK_WRITE_TEST,
    TASK_EXPLAIN_FAILURE, TASK_REVIEW_CODE, TASK_GENERATE_PLAN,
)
from agentx_evolve.model.model_registry import ModelRegistry
from agentx_evolve.model.json_output_validator import JsonOutputValidator
from agentx_evolve.model.prompt_runner import (
    PromptRunner, ModelRetryPolicy, BaseProvider, LocalProvider,
)

__all__ = [
    "ModelProfile", "PromptRequest", "ModelResponse", "ModelProviderConfig",
    "MP_SMALL_FAST", "MP_SMALL_CODER", "MP_MEDIUM_CODER", "MP_HOSTED_FALLBACK",
    "MD_SUCCESS", "MD_FAILED", "MD_INVALID_OUTPUT", "MD_INSUFFICIENT_CONTEXT", "MD_TIMEOUT", "MD_RATE_LIMITED",
    "TASK_IMPLEMENT_PATCH", "TASK_FIX_VALIDATION", "TASK_WRITE_TEST",
    "TASK_EXPLAIN_FAILURE", "TASK_REVIEW_CODE", "TASK_GENERATE_PLAN",
    "ModelRegistry", "JsonOutputValidator",
    "PromptRunner", "ModelRetryPolicy", "BaseProvider", "LocalProvider",
]
