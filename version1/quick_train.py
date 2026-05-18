#!/usr/bin/env python
"""Legacy convenience wrapper.

Phase 2 foundation standardizes training via the root entry point:

  python train.py --timesteps ... --save models/model_v1.zip

This file exists so the historical command `python version1/quick_train.py`
still works, but it simply forwards to `train.py`.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    project_root = Path(__file__).resolve().parents[1]
    train_py = project_root / "train.py"

    # Preserve legacy `--quick` flag by mapping to a smaller timesteps default
    # unless the user explicitly provided --timesteps.
    args = list(sys.argv[1:] if argv is None else argv)

    if "--timesteps" not in args:
        if "--quick" in args:
            args = [a for a in args if a != "--quick"]
            args.extend(["--timesteps", "10000"])
        else:
            # Historical script defaulted to a longer run; keep conservative here.
            args.extend(["--timesteps", "300000"])

    if "--save" not in args:
        args.extend(["--save", "models/model_v1.zip"])

    cmd = [sys.executable, str(train_py), *args]
    return subprocess.call(cmd)


if __name__ == "__main__":
    raise SystemExit(main())
