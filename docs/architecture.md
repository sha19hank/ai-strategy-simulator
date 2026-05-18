# Architecture

This repo is organized around a reproducible end-to-end experiment loop:

**train → evaluate → save artifacts → visualize**

## Components

### Environment
- `version1/env/market_env_multi_v1.py`
- PettingZoo `ParallelEnv` simulating a 3-firm oligopoly.
- Applies demand dynamics, market share allocation, regime switching, and supplier cost shocks.

### Training (canonical)
- `train.py`
- Provides a reproducible, CPU-only PPO training entry point.
- Trains three firm policies (firm_0..firm_2) and saves SB3 `.zip` artifacts.

### Experiment pipeline (canonical)
- `run_experiment.py`
- Orchestrates a full run:
  - calls training from `train.py` (no duplicated training logic)
  - evaluates with `version1/agents/eval_tournament.py`
  - writes artifacts to `results/run_YYYYMMDD_HHMMSS/`

### Evaluation
- `version1/agents/eval_tournament.py`
- Runs deterministic tournament rollouts and writes `tournament_results.csv`.
- Supports seeding for reproducible evaluation.

### Dashboard
- `dashboard/app.py`
- Reads `tournament_results.csv` and produces analysis + plots.

## Data flow (text diagram)

```
actions (price, R&D)
	|
	v
MarketEnvMultiV1 (economics + shocks)
	|
	v
rewards (profit) + observations (state)
	|
	v
PPO training (train.py)
	|
	v
saved models (.zip)
	|
	v
tournament evaluation (eval_tournament.py)
	|
	v
tournament_results.csv + metadata.json
	|
	v
dashboard (streamlit)
```

## Validation

Two layers of testing are expected to pass from repo root:
- `python -m pytest -q version1/tests/test_market_env_multi_v1.py`
- `python -m pytest -q tests/test_env_sanity.py`
