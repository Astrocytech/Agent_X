from enum import Enum


class PermissionClass(Enum):
    P0_READ_ONLY = "P0_READ_ONLY"
    P1_WRITE_SCRATCH = "P1_WRITE_SCRATCH"
    P2_WRITE_GENERATED = "P2_WRITE_GENERATED"
    P3_PROPOSE_PATCH = "P3_PROPOSE_PATCH"
    P4_MODIFY_NON_PROTECTED_CODE = "P4_MODIFY_NON_PROTECTED_CODE"
    P5_MODIFY_PROTECTED_CODE = "P5_MODIFY_PROTECTED_CODE"
    P6_DEPENDENCY_CHANGE = "P6_DEPENDENCY_CHANGE"
    P7_PUBLIC_API_CHANGE = "P7_PUBLIC_API_CHANGE"
    P8_RUNTIME_MUTATION = "P8_RUNTIME_MUTATION"
    P9_EXTERNAL_SIDE_EFFECT = "P9_EXTERNAL_SIDE_EFFECT"


_PROFILE_CEILINGS: dict[str, PermissionClass] = {
    "answer_seed": PermissionClass.P0_READ_ONLY,
    "research_seed": PermissionClass.P0_READ_ONLY,
    "coder_seed": PermissionClass.P3_PROPOSE_PATCH,
    "evaluator_seed": PermissionClass.P0_READ_ONLY,
    "evolution_proposer_seed": PermissionClass.P3_PROPOSE_PATCH,
    "coordinator_seed": PermissionClass.P1_WRITE_SCRATCH,
    "generalist": PermissionClass.P3_PROPOSE_PATCH,
}


def get_permission_ceiling(profile_id: str) -> PermissionClass:
    return _PROFILE_CEILINGS.get(profile_id, PermissionClass.P0_READ_ONLY)


def permission_allows(ceiling: PermissionClass, required: PermissionClass) -> bool:
    order = list(PermissionClass)
    return order.index(ceiling) >= order.index(required)
