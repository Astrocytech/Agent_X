from core_kernel.runtime.phases.prelude import (
    run_input_phase,
    run_goal_phase,
    run_profile_phase,
    run_task_phase,
    run_policy_phase,
)
from core_kernel.runtime.phases.decision import (
    run_planning_phase,
    run_governance_phase,
    run_approval_continuation_phase,
)
from core_kernel.runtime.phases.execution import run_tool_phase
from core_kernel.runtime.phases.record import (
    run_memory_phase,
    run_trace_phase,
    run_checkpoint_phase,
    run_evaluation_phase,
)
from core_kernel.runtime.phases.finale import run_output_phase

PHASE_PIPELINE = [
    ("input", run_input_phase),
    ("goal", run_goal_phase),
    ("profile", run_profile_phase),
    ("task", run_task_phase),
    ("policy", run_policy_phase),
    ("planning", run_planning_phase),
    ("governance", run_governance_phase),
    ("approval", run_approval_continuation_phase),
    ("tool", run_tool_phase),
    ("trace", run_trace_phase),
    ("evaluation", run_evaluation_phase),
    ("memory", run_memory_phase),
    ("checkpoint", run_checkpoint_phase),
    ("output", run_output_phase),
]
