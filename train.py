#!/usr/bin/env python
"""Phase 2 foundation: reproducible training entry point.

Goal:
  - A clean, CPU-only, end-to-end reproducible training command.
  - No fragile relative imports; runnable from repo root.

Usage:
  python train.py --timesteps 500000 --save models/model_v1.zip

What it produces:
  - Per-firm SB3 PPO models:
      models/model_v1_firm_0.zip
      models/model_v1_firm_1.zip
      models/model_v1_firm_2.zip
  - A bundle zip at the exact --save path containing the above + manifest:
      models/model_v1.zip
  - Copies in version1/experiments/models/ using eval_tournament.py naming
    so the existing evaluation pipeline works unchanged.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import sys
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict

import numpy as np


def _require_sb3():
    try:
        from stable_baselines3 import PPO  # noqa: F401
        return
    except Exception as exc:  # ImportError or binary deps
        raise RuntimeError(
            "Stable-Baselines3 is required for training. "
            "Install local dev deps with: pip install -r requirements-dev.txt"
        ) from exc


def seed_everything(seed: int) -> None:
    """Best-effort determinism across Python, NumPy, and Torch."""

    os.environ.setdefault("PYTHONHASHSEED", str(seed))

    random.seed(seed)
    np.random.seed(seed)

    try:
        import torch

        torch.manual_seed(seed)
        torch.cuda.manual_seed_all(seed)

        # Best-effort determinism on CPU.
        # Some configurations may not support full determinism; fall back gracefully.
        try:
            torch.use_deterministic_algorithms(True)
        except Exception:
            pass

        torch.set_num_threads(max(1, int(os.environ.get("OMP_NUM_THREADS", "1"))))
    except Exception:
        # Torch is a transitive dependency of SB3; if missing, SB3 import will fail anyway.
        pass


@dataclass
class TrainOutputs:
    seed: int
    timesteps_per_firm: int
    created_at_unix: int
    firm_models: Dict[str, str]
    bundle_zip: str
    eval_compat_dir: str


def _sb3_save(model, zip_path: Path) -> Path:
    """Save SB3 model ensuring the output path ends with .zip."""

    zip_path = zip_path.resolve()
    zip_path.parent.mkdir(parents=True, exist_ok=True)

    # SB3 expects path *without* .zip suffix
    if zip_path.suffix.lower() == ".zip":
        base = zip_path.with_suffix("")
    else:
        base = zip_path

    model.save(str(base))
    saved = base.with_suffix(".zip")

    if not saved.exists():
        raise RuntimeError(f"SB3 did not produce expected model file at {saved}")

    return saved


def train_three_firms(timesteps_per_firm: int, seed: int, device: str = "cpu"):
    _require_sb3()

    from stable_baselines3 import PPO
    from stable_baselines3.common.monitor import Monitor

    from version1.env.sb3_firm_env import PPOOpponent, SingleFirmMarketEnv

    # PPO hyperparameters: keep simple, defaults are acceptable but we pin the common ones.
    ppo_kwargs = dict(
        policy="MlpPolicy",
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        gae_lambda=0.95,
        clip_range=0.2,
        verbose=1,
        device=device,
    )

    models: Dict[str, PPO] = {}

    # Train sequentially to keep it minimal and reproducible.
    # Opponents use already-trained policies when available, else default random opponents.
    for idx in range(3):
        agent_name = f"firm_{idx}"

        opponents = {}
        for other_idx in range(3):
            other_agent = f"firm_{other_idx}"
            if other_agent == agent_name:
                continue
            if other_agent in models:
                opponents[other_agent] = PPOOpponent(models[other_agent])

        env = SingleFirmMarketEnv(
            controlled_agent=agent_name,
            opponents=opponents,
            env_kwargs={"n_firms": 3, "max_steps": 200},
            seed=seed + idx * 1_000,
        )
        env = Monitor(env)

        model = PPO(
            env=env,
            seed=seed + idx * 1_000,
            **ppo_kwargs,
        )

        model.learn(total_timesteps=int(timesteps_per_firm))
        models[agent_name] = model

        env.close()

    return models


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Train PPO policies for MarketEnvMultiV1 (reproducible, CPU-only).")
    parser.add_argument("--timesteps", type=int, default=500_000, help="Timesteps PER FIRM (sequential training).")
    parser.add_argument("--save", type=str, required=True, help="Output bundle path, e.g. models/model_v1.zip")
    parser.add_argument("--seed", type=int, default=123, help="Random seed for reproducibility")
    parser.add_argument("--device", type=str, default="cpu", choices=["cpu"], help="Training device (CPU only)")

    args = parser.parse_args(argv)

    seed_everything(int(args.seed))

    save_bundle_path = Path(args.save).resolve()
    save_bundle_path.parent.mkdir(parents=True, exist_ok=True)

    # Derive per-firm save paths based on the bundle name
    base_stem = save_bundle_path.stem
    base_dir = save_bundle_path.parent

    per_firm_paths = {
        "firm_0": base_dir / f"{base_stem}_firm_0.zip",
        "firm_1": base_dir / f"{base_stem}_firm_1.zip",
        "firm_2": base_dir / f"{base_stem}_firm_2.zip",
    }

    print("=" * 70)
    print("AI Strategy Simulator | Phase 2 | Reproducible Training")
    print("=" * 70)
    print(f"Seed: {args.seed}")
    print(f"Timesteps per firm: {args.timesteps:,}")
    print(f"Bundle output: {save_bundle_path}")
    print()

    started = time.time()
    models = train_three_firms(timesteps_per_firm=int(args.timesteps), seed=int(args.seed), device=args.device)
    elapsed = time.time() - started

    # Save per-firm SB3 models
    saved_firm_files: Dict[str, Path] = {}
    for agent, model in models.items():
        saved = _sb3_save(model, per_firm_paths[agent])
        saved_firm_files[agent] = saved

    # Also write eval-tournament compatible copies into version1/experiments/models
    eval_dir = Path("version1/experiments/models").resolve()
    eval_dir.mkdir(parents=True, exist_ok=True)
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    for agent, src_path in saved_firm_files.items():
        dst_path = eval_dir / f"{agent}_{timestamp}.zip"
        shutil.copy2(src_path, dst_path)

    # Create bundle zip at --save containing all firm zips + manifest
    outputs = TrainOutputs(
        seed=int(args.seed),
        timesteps_per_firm=int(args.timesteps),
        created_at_unix=int(time.time()),
        firm_models={k: str(v) for k, v in saved_firm_files.items()},
        bundle_zip=str(save_bundle_path),
        eval_compat_dir=str(eval_dir),
    )

    with zipfile.ZipFile(save_bundle_path, mode="w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("manifest.json", json.dumps(asdict(outputs), indent=2))
        for agent, model_path in saved_firm_files.items():
            zf.write(model_path, arcname=f"sb3_models/{model_path.name}")

    print()
    print("✓ Training complete")
    print(f"Elapsed: {elapsed/60.0:.1f} min")
    print("Saved:")
    for agent, path in saved_firm_files.items():
        print(f"  - {agent}: {path}")
    print(f"  - bundle: {save_bundle_path}")
    print(f"  - eval-compatible copies: {eval_dir}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
