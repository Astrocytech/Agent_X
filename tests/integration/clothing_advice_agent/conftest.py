import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent.parent.parent
EXAMPLES = ROOT / "examples"
L0_CODE = ROOT / "L0" / "CODE"
for p in [str(EXAMPLES), str(L0_CODE)]:
    if p not in sys.path:
        sys.path.insert(0, p)
