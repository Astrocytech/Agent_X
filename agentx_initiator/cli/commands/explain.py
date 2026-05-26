from pathlib import Path
from agentx_initiator.core.paths import repo_root


def register(sub):
    p = sub.add_parser("explain", help="Explain a file, directory, or layer")
    p.add_argument("path", nargs="?", default=".", help="Path to explain (relative to repo root)")
    p.set_defaults(func=run)


def run(args):
    root = repo_root()
    target = root / args.path
    if not target.exists():
        print(f"Error: path does not exist: {args.path}")
        return

    relative = target.relative_to(root) if target != root else Path(".")

    if target.is_file():
        print(f"File: {relative}")
        print(f"  Size: {target.stat().st_size} bytes")
        print(f"  Extension: {target.suffix}")
        _explain_file(target)

    elif target.is_dir():
        files = list(target.rglob("*"))
        dirs = [d for d in files if d.is_dir()]
        regular = [f for f in files if f.is_file()]
        print(f"Directory: {relative}")
        print(f"  Subdirectories: {len(dirs)}")
        print(f"  Files: {len(regular)}")
        print(f"  Layer: {_detect_layer(relative)}")

        py_files = [f for f in regular if f.suffix == ".py"]
        if py_files:
            print(f"  Python modules: {len(py_files)}")
            for pf in py_files[:5]:
                print(f"    - {pf.relative_to(root)}")


def _explain_file(path: Path):
    text = path.read_text()
    lines = text.splitlines()
    print(f"  Lines: {len(lines)}")

    if path.suffix == ".py":
        classes = [l for l in lines if l.strip().startswith("class ")]
        funcs = [l for l in lines if l.strip().startswith("def ")]
        if classes:
            print(f"  Classes: {[c.split()[1].split('(')[0] for c in classes]}")
        if funcs:
            print(f"  Functions: {[f.split()[1].split('(')[0] for f in funcs]}")

    if path.suffix == ".md":
        headings = [l.strip("# ") for l in lines if l.strip().startswith("#")]
        if headings:
            print(f"  Headings: {len(headings)}")
            for h in headings[:5]:
                print(f"    - {h}")


def _detect_layer(relative: Path) -> str:
    parts = relative.parts
    for p in parts:
        if p.startswith("L") and len(p) >= 2 and p[1].isdigit():
            return p
    return "root"
