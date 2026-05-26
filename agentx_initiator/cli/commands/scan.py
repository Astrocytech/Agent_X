import json
from agentx_initiator.core.repo_scanner import scan_repo
from agentx_initiator.core.paths import snapshot_file, ensure_state_dirs
from agentx_initiator.core.audit_log import append_event


def register(sub):
    p = sub.add_parser("scan", help="Scan repository structure and layers")
    p.set_defaults(func=run)


def run(args):
    ensure_state_dirs()
    scan = scan_repo()

    snap = snapshot_file("repo_scan_latest.json")
    snap.write_text(scan.model_dump_json(indent=2))

    print(f"Repository: {scan.root}")
    print(f"Total files: {scan.total_files}")
    print(f"  Source: {scan.source_files}")
    print(f"  Docs:   {scan.doc_files}")
    print(f"  Tests:  {scan.test_files}")
    print()
    for layer in scan.layers:
        status = "✓" if layer.has_readme else "✗"
        print(f"  {status} {layer.layer}: {layer.file_count} files — {layer.purpose}")

    append_event({
        "event_type": "scan",
        "detail": f"Scanned {scan.total_files} files across {len(scan.layers)} layers",
    })
