#!/usr/bin/env bash
set -euo pipefail

# Clean checkout proof for prove-functional-agentx
# Clones the repo to a temp dir and runs the full proof chain
# Avoids reusing runtime reports from the active checkout

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "=== prove-functional-agentx-clean-checkout ==="
echo "Source repo: $REPO_ROOT"

tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

echo "Cloning to $tmpdir"
git clone "$REPO_ROOT" "$tmpdir/Agent_X"
cd "$tmpdir/Agent_X"

HEAD_SHA=$(git rev-parse HEAD)
echo "HEAD: $HEAD_SHA"

git checkout -q "$HEAD_SHA"
git clean -xfd

echo "Installing dependencies"
pip3 install -q -r requirements/seed.txt 2>/dev/null || true
pip3 install -q -r requirements/test.txt 2>/dev/null || true

echo "Running make prove-functional-agentx"
make prove-functional-agentx

echo ""
echo "=== Clean checkout proof: PASS ==="
echo "HEAD: $HEAD_SHA"
