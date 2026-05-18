# Overview

AI Strategy Simulator is a research-oriented reinforcement learning + economic simulation project for studying **emergent firm behavior** in a regulated, innovation-driven **oligopoly**.

## What it does
- Simulates a 3-firm market where each firm chooses:
  - **price**
  - **R&D investment** (innovation)
- Applies realistic exogenous dynamics:
  - demand responds to price and substitutes
  - Markov boom/recession regimes
  - supplier cost shocks (marginal cost volatility)
- Produces **reproducible experiments**: train → evaluate → saved artifacts → dashboard visualization.

## Key entry points
- Training (canonical): `train.py`
- End-to-end experiments (canonical): `run_experiment.py`
- Environment (V1): `version1/env/market_env_multi_v1.py`
- Evaluation (tournament): `version1/agents/eval_tournament.py`
- Dashboard: `dashboard/app.py`

## Reproducibility
- Experiments are seeded end-to-end (training + evaluation).
- Environment correctness is enforced by tests:
  - `version1/tests/test_market_env_multi_v1.py`
  - `tests/test_env_sanity.py` (sanity + robustness)

## Dependencies
Two install modes are supported:
- **Local development / training + dashboard + tests**:
  - `pip install -r requirements-dev.txt`
- **Dashboard-only (deployment)**:
  - `pip install -r requirements.txt`

## Versioning
- **Version 1** is the active, working system.
- **Version 2** is scaffolding for future extensions (not a stable training/eval target yet).

## Next reading
- Experiments: see `docs/experiment_guide.md`
- Architecture: see `docs/architecture.md`
- Environment economics & constraints: see `docs/environment.md`
- Full economic specification: see `docs/ECONOMICS.md`
