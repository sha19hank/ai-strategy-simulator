# Experiment Guide

This project’s canonical workflow is:

- **train** → **evaluate** → write artifacts under `results/run_YYYYMMDD_HHMMSS/` → **visualize**

The single command entry point is `run_experiment.py`.

## Quick run (recommended)

From repo root:

```bash
pip install -r requirements-dev.txt
python run_experiment.py --timesteps 500000 --seed 123
streamlit run dashboard/app.py
```

## What `run_experiment.py` does

1. Seeds RNGs for reproducibility
2. Trains three firm policies (PPO) using the canonical training logic from `train.py`
3. Evaluates the newly trained policies via the tournament evaluator
4. Writes outputs into a new run folder

## Output layout

Each experiment creates:

```
results/
  run_YYYYMMDD_HHMMSS/
    models/
      model_v1_firm_0.zip
      model_v1_firm_1.zip
      model_v1_firm_2.zip
    tournament_results.csv
    metadata.json
```

## `metadata.json`

`metadata.json` is designed to be lightweight and machine-readable.

Current fields:
- `timesteps`: timesteps per firm
- `seed`: experiment seed
- `timestamp`: run timestamp
- `model_paths`: relative paths to saved SB3 `.zip` artifacts

Example:

```json
{
  "timesteps": 500000,
  "seed": 123,
  "timestamp": "20260518_171830",
  "model_paths": {
    "firm_0": "models/model_v1_firm_0.zip",
    "firm_1": "models/model_v1_firm_1.zip",
    "firm_2": "models/model_v1_firm_2.zip"
  }
}
```

## Evaluation artifacts

`tournament_results.csv` contains per-step logs for each firm, including:
- price, marginal cost, market share
- quantities and profit
- demand and regime indicators

The dashboard reads this CSV and generates summary analytics.

## Running tests

From repo root:

```bash
python -m pytest -q version1/tests/test_market_env_multi_v1.py
python -m pytest -q tests/test_env_sanity.py
```
