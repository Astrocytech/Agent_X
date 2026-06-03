from .acceptance_models import (
    FinalAcceptanceLayer, MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
)

_ALL_MODES = [
    MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
    MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
]

_CATALOG_DATA = [
    {
        "layer_id": "L0_SEED_KERNEL",
        "layer_name": "L0 Seed Kernel",
        "roadmap_number": 0,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "L1_STANDARDS_FRAMEWORK",
        "layer_name": "L1 Standards Framework Contracts",
        "roadmap_number": 1,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "L2_PROFILES_DOCS",
        "layer_name": "L2 Profiles SIB ES EQC Docs",
        "roadmap_number": 2,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "AGENTX_INITIATOR",
        "layer_name": "Agent X Initiator",
        "roadmap_number": 3,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "SECURITY_SANDBOX",
        "layer_name": "Security Sandbox Filesystem Boundary",
        "roadmap_number": 4,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "POLICY_CAPABILITY_REGISTRY",
        "layer_name": "Policy Capability Registry",
        "roadmap_number": 5,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "GOVERNED_PATCH_EXECUTION",
        "layer_name": "Governed Patch Execution",
        "roadmap_number": 6,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "FAILURE_TAXONOMY",
        "layer_name": "Failure Taxonomy Recovery Playbook",
        "roadmap_number": 7,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "TOOL_MCP_ADAPTER",
        "layer_name": "Tool MCP Adapter",
        "roadmap_number": 8,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "MODEL_ADAPTER",
        "layer_name": "Model Adapter",
        "roadmap_number": 9,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "LOCAL_MODEL_RUNTIME_PROFILE",
        "layer_name": "Local Model Runtime Profile",
        "roadmap_number": 10,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "CONTEXT_BUILDER_TASK_PACKER",
        "layer_name": "Context Builder Task Packer",
        "roadmap_number": 11,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "PROMPT_CONTRACT_VERSIONING",
        "layer_name": "Prompt Contract Versioning",
        "roadmap_number": 12,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "LLM_IMPLEMENTATION_WORKER",
        "layer_name": "LLM Implementation Worker",
        "roadmap_number": 13,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "SELF_EVOLUTION_ORCHESTRATOR",
        "layer_name": "Self Evolution Orchestrator",
        "roadmap_number": 14,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "HUMAN_REVIEW_APPROVAL",
        "layer_name": "Human Review Approval Interface",
        "roadmap_number": 15,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "PROMOTION_RELEASE_GATE",
        "layer_name": "Promotion Release Gate",
        "roadmap_number": 16,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "GIT_INTEGRATION",
        "layer_name": "Git Integration",
        "roadmap_number": 17,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "EVALUATION_HARNESS",
        "layer_name": "Evaluation Harness Regression Benchmark",
        "roadmap_number": 18,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
    {
        "layer_id": "LONG_TERM_LEARNING",
        "layer_name": "Long Term Learning Outcome Review",
        "roadmap_number": 19,
        "required_for_acceptance": False,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": _ALL_MODES,
    },
    {
        "layer_id": "DOCUMENTATION_SYNC",
        "layer_name": "Documentation Synchronization",
        "roadmap_number": 20,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE, MODE_NON_PRODUCTION_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "TASK_QUEUE_SESSION_SCHEDULER",
        "layer_name": "Task Queue Session Scheduler",
        "roadmap_number": 21,
        "required_for_acceptance": False,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [],
        "deferral_modes_allowed": _ALL_MODES,
    },
    {
        "layer_id": "MONITORING_OBSERVABILITY",
        "layer_name": "Monitoring Observability",
        "roadmap_number": 22,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [
            MODE_PRODUCTION_ACCEPTANCE, MODE_RELEASE_ACCEPTANCE,
        ],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE, MODE_NON_PRODUCTION_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "PACKAGING_DISTRIBUTION",
        "layer_name": "Packaging Distribution",
        "roadmap_number": 23,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [MODE_RELEASE_ACCEPTANCE],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "BACKUP_DISASTER_RECOVERY",
        "layer_name": "Backup Disaster Recovery",
        "roadmap_number": 24,
        "required_for_acceptance": True,
        "safe_deferral_allowed": True,
        "acceptance_modes_required": [MODE_RELEASE_ACCEPTANCE],
        "deferral_modes_allowed": [
            MODE_IMPLEMENTATION_ACCEPTANCE, MODE_SOURCE_ONLY_ACCEPTANCE,
            MODE_NON_PRODUCTION_ACCEPTANCE, MODE_PRODUCTION_ACCEPTANCE,
        ],
    },
    {
        "layer_id": "FINAL_SYSTEM_ACCEPTANCE",
        "layer_name": "Final System Acceptance",
        "roadmap_number": 25,
        "required_for_acceptance": True,
        "safe_deferral_allowed": False,
        "bootstrap_self_layer": True,
        "acceptance_modes_required": _ALL_MODES,
        "deferral_modes_allowed": [],
    },
]


def build_canonical_layer_catalog() -> list[FinalAcceptanceLayer]:
    layers: list[FinalAcceptanceLayer] = []
    for data in _CATALOG_DATA:
        layers.append(_dict_to_layer(data))
    return layers


def _dict_to_layer(data: dict) -> FinalAcceptanceLayer:
    return FinalAcceptanceLayer(
        layer_id=data["layer_id"],
        layer_name=data["layer_name"],
        roadmap_number=data["roadmap_number"],
        required_for_acceptance=data["required_for_acceptance"],
        safe_deferral_allowed=data["safe_deferral_allowed"],
        acceptance_modes_required=data.get("acceptance_modes_required", []),
        deferral_modes_allowed=data.get("deferral_modes_allowed", []),
        expected_evidence_aliases=data.get("expected_evidence_aliases", []),
        stale_after_days=data.get("stale_after_days"),
        bootstrap_self_layer=data.get("bootstrap_self_layer", False),
    )


def validate_layer_catalog(layers: list[FinalAcceptanceLayer]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for layer in layers:
        if layer.layer_id in seen_ids:
            errors.append(f"Duplicate layer_id: {layer.layer_id}")
        seen_ids.add(layer.layer_id)
        if not layer.layer_id:
            errors.append("Layer with empty layer_id found")
        if not layer.layer_name:
            errors.append(f"Layer {layer.layer_id} has empty layer_name")
    if not any(l.layer_id == "FINAL_SYSTEM_ACCEPTANCE" for l in layers):
        errors.append("FINAL_SYSTEM_ACCEPTANCE layer missing from catalog")
    return errors
