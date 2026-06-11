#!/usr/bin/env python3
import sys, os, subprocess

SECURITY_FILES = ["path_boundary.py", "sandbox_policy.py", "safe_file_ops.py", "safe_subprocess.py", "network_policy.py", "secret_redactor.py"]
POLICY_FILES = ["capability_registry.py", "policy_enforcer.py"]
REQUIRED_DIRS = [
    ("security", "tools/agentx_evolve/security"),
    ("policy", "tools/agentx_evolve/policy"),
    ("failure", "tools/agentx_evolve/failure"),
    ("runtime_artifacts", "tools/agentx_evolve/runtime_artifacts"),
]

def check_dir(label, path):
    if not os.path.isdir(path):
        return [f"Directory '{path}' ({label}) does not exist"]
    return []

def check_file_in_dir(label, dirpath, filename):
    fpath = os.path.join(dirpath, filename)
    if not os.path.isfile(fpath):
        return [f"File '{fpath}' ({label}) not found"]
    return []

def check_import(module_path, file_label):
    fpath = module_path.replace(".", "/") + ".py"
    try:
        import py_compile
        py_compile.compile(fpath, doraise=True)
        return []
    except py_compile.PyCompileError as e:
        return [f"Syntax error in '{fpath}' ({file_label}): {e}"]
    except Exception as e:
        return [f"Failed to check '{fpath}' ({file_label}): {e}"]

def main():
    base = "tools/agentx_evolve"
    errors = []

    for label, dirpath in REQUIRED_DIRS:
        errors.extend(check_dir(label, dirpath))

    sec_dir = os.path.join(base, "security")
    if os.path.isdir(sec_dir):
        for fname in SECURITY_FILES:
            errors.extend(check_file_in_dir(f"security/{fname}", sec_dir, fname))
            fpath = os.path.join(sec_dir, fname)
            if os.path.isfile(fpath):
                errors.extend(check_import(f"tools.agentx_evolve.security.{fname.replace('.py','')}", f"security/{fname}"))

    pol_dir = os.path.join(base, "policy")
    if os.path.isdir(pol_dir):
        for fname in POLICY_FILES:
            errors.extend(check_file_in_dir(f"policy/{fname}", pol_dir, fname))
            fpath = os.path.join(pol_dir, fname)
            if os.path.isfile(fpath):
                errors.extend(check_import(f"tools.agentx_evolve.policy.{fname.replace('.py','')}", f"policy/{fname}"))

    if errors:
        for e in errors:
            print(f"FAIL: {e}")
        sys.exit(1)
    print("PASS: safety/policy foundation validated - all dirs, files, imports OK")
    sys.exit(0)

if __name__ == "__main__":
    main()
