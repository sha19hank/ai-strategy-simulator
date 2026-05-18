#!/usr/bin/env python
"""End-to-end experiment runner (Phase 2 / Step 2).

Pipeline:
  train -> evaluate -> write tournament_results.csv

Usage:
  python run_experiment.py --timesteps 500000 --seed 123

Outputs:
  results/
    run_YYYYMMDD_HHMMSS/
      models/
        model_v1_firm_0.zip
        model_v1_firm_1.zip
        model_v1_firm_2.zip
      tournament_results.csv
      metadata.json

Design constraints:
- Do NOT duplicate training logic: import from train.py
- Use existing evaluation logic from version1/agents/eval_tournament.py
- CPU-only
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, Tuple


@dataclass
class ExperimentMetadata:
    timesteps: int
    seed: int
    timestamp: str
    model_paths: Dict[str, str]


def _timestamp() -> str:
    return time.strftime("%Y%m%d_%H%M%S")


def train_models(*, timesteps: int, seed: int, models_dir: Path):
    """Train PPO agents and save SB3 model zips into models_dir.

    Returns:
      models: Dict[str, PPO]
      saved_paths: Dict[str, Path]
    """

    from train import seed_everything, train_three_firms, _sb3_save

    seed_everything(seed)

    models_dir.mkdir(parents=True, exist_ok=True)

    # Train (returns in-memory SB3 PPO models keyed by firm_0..firm_2)
    models = train_three_firms(timesteps_per_firm=timesteps, seed=seed, device="cpu")

    # Save per-firm model zips
    saved_paths: Dict[str, Path] = {}
    for firm in ["firm_0", "firm_1", "firm_2"]:
        out_path = models_dir / f"model_v1_{firm}.zip"
        saved_paths[firm] = _sb3_save(models[firm], out_path)

    return models, saved_paths


def evaluate_models(*, models, seed: int, output_dir: Path):
    """Run tournament evaluation and write tournament_results.csv into output_dir."""

    from version1.agents.eval_tournament import run_tournament

    output_dir.mkdir(parents=True, exist_ok=True)

    # Use newly trained in-memory models; do NOT load from global directories.
    logs_df = run_tournament(
        models=models,
        n_episodes=10,
        max_steps=200,
        output_dir=str(output_dir),
        render=False,
        seed=seed,
    )

    csv_path = output_dir / "tournament_results.csv"
    if not csv_path.exists():
        raise RuntimeError(f"Evaluation did not produce expected CSV at {csv_path}")

    return logs_df, csv_path


def save_results(*, run_dir: Path, metadata: ExperimentMetadata):
    """Write metadata.json into run_dir."""

    run_dir.mkdir(parents=True, exist_ok=True)

    meta_path = run_dir / "metadata.json"
    meta_path.write_text(json.dumps(asdict(metadata), indent=2), encoding="utf-8")

    return meta_path


def run_experiment(*, timesteps: int, seed: int, results_root: Path = Path("results")) -> Tuple[Path, Path, Path]:
    """Run the full pipeline.

    Returns:
      run_dir, tournament_csv_path, metadata_path
    """

    ts = _timestamp()
    run_dir = (results_root / f"run_{ts}").resolve()
    models_dir = run_dir / "models"

    # 1) Train + save models
    models, saved_paths = train_models(timesteps=timesteps, seed=seed, models_dir=models_dir)

    # 2) Evaluate + write CSV
    _, tournament_csv_path = evaluate_models(models=models, seed=seed, output_dir=run_dir)

    # 3) Write metadata
    metadata = ExperimentMetadata(
        timesteps=int(timesteps),
        seed=int(seed),
        timestamp=ts,
        model_paths={
            k: str(Path(v).resolve().relative_to(run_dir)) for k, v in saved_paths.items()
        },
    )
    metadata_path = save_results(run_dir=run_dir, metadata=metadata)

    return run_dir, tournament_csv_path, metadata_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a full AI Strategy Simulator experiment (train -> evaluate).")
    parser.add_argument("--timesteps", type=int, required=True, help="Timesteps PER FIRM")
    parser.add_argument("--seed", type=int, required=True, help="Random seed")

    args = parser.parse_args(argv)

    try:
        run_dir, csv_path, meta_path = run_experiment(timesteps=args.timesteps, seed=args.seed)
    except Exception as exc:
        raise SystemExit(f"❌ Experiment failed: {exc}") from exc

    print("=" * 70)
    print("✅ Experiment complete")
    print(f"Run directory: {run_dir}")
    print(f"Models: {run_dir / 'models'}")
    print(f"Tournament CSV: {csv_path}")
    print(f"Metadata: {meta_path}")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
