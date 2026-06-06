import warnings
from agentx_evolve.docs_sync.doc_registry import (
    classify_document_type, classify_document_authority,
    extract_document_id, extract_component_id, extract_version,
    has_generated_markers, is_protected_document,
)
warnings.warn(
    "agentx_evolve.docs_sync.doc_classifier is deprecated; "
    "use agentx_evolve.docs_sync.doc_registry instead",
    DeprecationWarning, stacklevel=2,
)

__all__ = [
    "classify_document_type", "classify_document_authority",
    "extract_document_id", "extract_component_id", "extract_version",
    "has_generated_markers", "is_protected_document",
]
