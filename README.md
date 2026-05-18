# AI Strategy Simulator

Research-grade reinforcement learning + economic simulation for studying **emergent competitive strategy** in a regulated, innovation-driven **3-firm oligopoly**.

## What problem this solves
- Gives a controllable simulation environment where firms learn pricing + innovation strategy under:
  - demand elasticity
  - cost shocks
  - economic regimes (boom/recession)
  - substitutes pressure
- Produces **reproducible experiments** (seeded training + seeded evaluation) with artifacts you can audit and visualize.

## Key features
- Multi-agent market simulation (PettingZoo ParallelEnv)
- Reproducible training (`train.py`, CPU-only)
- End-to-end experiment runner (`run_experiment.py`)
- Tournament evaluation (`version1/agents/eval_tournament.py`)
- Streamlit dashboard (`dashboard/app.py`)
- Environment sanity + robustness test suite (`tests/test_env_sanity.py`)

## Quick start

From repo root:

```bash
pip install -r requirements-dev.txt
python run_experiment.py --timesteps 500000 --seed 123
streamlit run dashboard/app.py
```

## Example outputs

Running `run_experiment.py` creates:

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

## Project structure (high level)

```
ai-strategy-simulator/
├── train.py                      # canonical reproducible training
├── run_experiment.py              # train → evaluate → save results
├── tests/
│   └── test_env_sanity.py         # economic + numerical robustness suite
├── version1/
│   ├── env/
│   │   ├── market_env_multi_v1.py # oligopoly environment (V1)
│   │   └── sb3_firm_env.py        # minimal SB3 wrapper for training
│   ├── agents/
│   │   └── eval_tournament.py     # deterministic tournament + CSV logging
│   └── tests/
│       └── test_market_env_multi_v1.py
├── dashboard/
│   └── app.py                    # streamlit dashboard
└── docs/
    ├── overview.md
    ├── architecture.md
    ├── experiment_guide.md
    ├── environment.md
    └── ECONOMICS.md               # full economic specification
```

## Running tests

```bash
python -m pytest -q version1/tests/test_market_env_multi_v1.py
python -m pytest -q tests/test_env_sanity.py
```

## Documentation

- Start here: `docs/overview.md`
- How to run experiments: `docs/experiment_guide.md`
- System layout: `docs/architecture.md`
- Environment economics + constraints: `docs/environment.md`
- Full model spec: `docs/ECONOMICS.md`
