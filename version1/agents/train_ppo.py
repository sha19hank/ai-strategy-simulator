"""Legacy script kept for backward compatibility.

Historically this referenced a wrapper (`version1.env.v1_wrappers`) that no longer
exists in the repo. Phase 2 foundation standardizes training via the root
entry point:

  python train.py --timesteps ... --save models/model_v1.zip

This file now redirects to that canonical entry point.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    project_root = Path(__file__).resolve().parents[2]
    train_py = project_root / "train.py"
    cmd = [sys.executable, str(train_py)]
    if argv is None:
        cmd.extend(sys.argv[1:])
    else:
        cmd.extend(argv)
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
