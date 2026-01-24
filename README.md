# AI Strategy Simulator

**Computational Economics Platform for Emergent Competitive Strategy in Oligopolistic Markets**

## Project Vision

We are building a research-grade multi-agent reinforcement learning (MARL) system to study how autonomous firms learn competitive strategy in regulated, innovation-driven markets.

The simulator models an oligopolistic industry (manufacturing/pharmaceutical) where 3 AI-controlled players compete on **price** and **innovation (R&D)**, subject to **cost structure**, **regulation**, and **market dynamics**.

**Research Goal:** Understand emergent pricing equilibria, innovation races, market concentration, and strategic retaliation in computational economies.

---

## Architecture Overview

```
MarketEnvMultiV1 (PettingZoo ParallelEnv)
    ↓
3 Independent PPO Agents (Stable-Baselines3)
    ↓
Self-Play Learning Loop
    ↓
Tournament Evaluation
    ↓
Dashboard Visualization
```

- **Environment:** Fully specified oligopoly market with exogenous shocks
- **Learning:** True multi-agent self-play (no single-agent shortcuts)
- **Outcomes:** Emergent behavior (we observe, don't prescribe)
- **Research:** Publication-ready analysis pipeline

---

## Version 1: Foundation (Complete)

**Status:** ✅ Training validated, economics calibrated, ready for dashboard

**Deliverable:**
- ✅ Clean multi-agent market environment (MarketEnvMultiV1)
- ✅ Self-play PPO training (1M timesteps)
- ✅ Evaluation + tournament system (10 episodes × 200 steps)
- ✅ Economic simulation (200 steps = 50 years)
- ✅ Analysis pipeline with price war detection

**Economics:**
- Profit maximization: `π_i = P_i·Q_i − C_m·Q_i − k·(R&D)² − C_capital − C_compliance`
- Market share: Softmax competition (α=0.05 price sensitivity, β=1.5 innovation power)
- Regulation: Price cap ($250), compliance cost
- Shocks: Markov economic cycles, supplier volatility, substitute pressure
- Innovation: Stock accumulation with quadratic cost, diminishing returns

**Latest Results (Jan 24, 2026):**
- Innovation leader emerged: 72% market share, $8,817 profit
- Realistic monopolization via R&D investment
- Perfect price coordination at $82 (implicit collusion)
- HHI = 0.37 (high concentration, matches real pharma/tech markets)

**See:** `docs/ECONOMICS.md` for full specification

---

## Version 2: Extensions (Future)

**Planned additions:**
- Human-AI competitive play (twin-agent system)
- Bankruptcy mechanics (firm exit)
- Market entry (firm injection)
- Real data calibration
- Policy analysis

---

## Project Structure

```
ai-strategy-simulator/
├── README.md                              (this file)
├── DEVELOPMENT_LOG.md                     (progress tracking)
├── requirements.txt                       (dependencies)
├── docs/
│   └── ECONOMICS.md                       (economic specification)
├── core/
│   └── models/                            (core economic functions)
├── version1/
│   ├── env/
│   │   ├── market_env_multi_v1.py         (clean MARL environment)
│   │   └── v1_wrappers.py                 (SB3 integration)
│   ├── agents/
│   │   ├── train_marl.py                  (self-play training)
│   │   ├── eval_tournament.py             (evaluation)
│   │   └── agent_utils.py
│   ├── experiments/
│   │   ├── logs/                          (training logs)
│   │   └── models/                        (trained agents)
│   └── tests/
│       └── test_market_env.py
└── version2/
    ├── twin_env/                          (human-AI environment)
    ├── agents/                            (competitive agents)
    └── tests/
```

---

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Tests
```bash
pytest version1/tests/ -v
```

### 3. Train Agents (Self-Play)
```bash
python -m version1.agents.train_marl
```

### 4. Evaluate & Analyze
```bash
python -m version1.agents.eval_tournament
```

### 5. View Results
```bash
streamlit run dashboard/app.py
```

---

## Key Features

✅ **True Multi-Agent RL**
- 3 independent PPO agents learning simultaneously
- Self-play (agents learn from each other)
- No centralized controller

✅ **Grounded Economics**
- Bertrand oligopoly model
- Industrial organization theory (Porter's 5 Forces)
- Realistic cost structure + regulation

✅ **Emergent Behavior**
- Price wars (not prescribed)
- Innovation races (not scripted)
- Market concentration (natural outcome)
- Strategic retaliation (learned strategy)

✅ **Research Quality**
- Reproducible experiments
- Publication pipeline
- Policy analysis capability
- Extensible architecture

---

## Research Questions

This system enables study of:

1. **How do autonomous firms learn competitive strategy?**
2. **What pricing equilibria emerge naturally?**
3. **When do price wars occur? Why?**
4. **How does innovation create dominance?**
5. **What is the impact of regulation on market structure?**
6. **How do cost shocks reshape competitive dynamics?**
7. **Can tacit collusion emerge without coordination?**
8. **How does market concentration evolve over time?**

---

## Documentation

- **DEVELOPMENT_LOG.md** — Progress tracking & session notes
- **docs/ECONOMICS.md** — Full economic specification (parameters, equations, dynamics)
- **version1/tests/** — Environment validation tests

---

## Status

| Phase | Status | Notes |
|-------|--------|-------|
| **Economics** | ✅ Complete | Calibrated α=0.05, β=1.5, validated realistic |
| **Environment** | ✅ Complete | MarketEnvMultiV1, 14/14 tests passing |
| **Training** | ✅ Complete | 1M-step self-play, monopolization emerged |
| **Evaluation** | ✅ Complete | Tournament analysis with price war detection |
| **Dashboard** | 🔨 Next | Update to MarketEnvMultiV1 API |
| **Research** | ⏳ Ready | Publication-ready economics, awaiting viz |

---

## Contact & Attribution

**Project Lead:** Computational Economics Research

**Framework Stack:**
- PettingZoo (multi-agent environment)
- Stable-Baselines3 (PPO algorithm)
- Streamlit (visualization)
- NumPy/SciPy (computation)

---

**Last Updated:** January 24, 2026

**Latest:** Economic calibration complete, training validated, monopolization realistic

**Next Build:** Dashboard visualization for tournament results
