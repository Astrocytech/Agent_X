from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.paths import snapshot_file, report_file, ensure_state_dirs, state_dir
from agentx_initiator.core.report_writer import render_report, write_report
from agentx_initiator.core.architecture_analyzer import analyze_architecture
from agentx_initiator.core.audit_log import append_event


def register(sub):
    p = sub.add_parser("status", help="Generate status report")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    scan = scan_repo()
    arch = analyze_architecture()

    snap = snapshot_file("architecture_latest.json")
    snap.write_text(arch.model_dump_json(indent=2))

    arch_dir = state_dir() / "architecture"
    arch_dir.mkdir(parents=True, exist_ok=True)

    context = {
        "repo_scan": scan,
        "architecture": arch,
        "layers": len(arch.layers),
        "layer_count": arch.layer_count,
        "valid_layer_structure": arch.valid_layer_structure,
        "l0_independent": arch.l0_independent,
        "l1_separated": arch.l1_separated,
        "l2_contains_active_runtime": arch.l2_contains_active_runtime,
        "risks": arch.risks,
        "passed": 0,
        "failed": 0,
        "governance_checks": [],
    }

    report = render_report("status_report.md.j2", context)
    path = write_report("latest_status.md", report)

    print(f"Status report written to {path}")
    print(f"Layers: {arch.layer_count}")
    print(f"  L0 independent: {arch.l0_independent}")
    print(f"  L1 separated: {arch.l1_separated}")
    for layer in arch.layers:
        print(f"  {layer.layer}: {layer.file_count} files")

    append_event({
        "event_type": "status",
        "detail": f"Status report: {arch.layer_count} layers, {scan.total_files} files",
    })
