"""Legacy entry point (kept for backward compatibility).

This module previously contained a non-reproducible loop (it called `model.predict`
but never actually updated policies with `model.learn`). It also used a broken
relative import (`from env...`).

Phase 2 foundation introduces a clean, reproducible root entry point:

    python train.py --timesteps ... --save models/model_v1.zip

To avoid duplicate / divergent training logic, this file now redirects to that
entry point.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main(argv: list[str] | None = None) -> int:
    """Redirect to the canonical training entry point at repo root."""
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


if __name__ == "__main__":
    # Train agents
    models, envs = train_self_play(
        total_timesteps=300000,
        n_envs=4,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
    )
    
    print("\n✅ Training complete.")
