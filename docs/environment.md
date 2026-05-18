# Environment (V1)

The active environment is `MarketEnvMultiV1`, implemented in `version1/env/market_env_multi_v1.py`.

## Economic model (high level)
Each firm chooses an action each step:
- `price`
- `R&D investment`

The environment computes:
- **effective demand** (macro regime × price elasticity × substitute pressure)
- **market shares** via softmax competition on price + innovation
- **quantities** per firm: `Q_i = share_i * demand`
- **profit** per firm: revenue minus marginal, R&D, capital, and compliance costs

For the full specification and parameter rationale, see `docs/ECONOMICS.md`.

## Key state variables
- `prices[i]`: firm i’s price
- `marginal_costs[i]`: firm i’s current marginal cost (after supplier shock)
- `innovation_stocks[i]`: cumulative innovation stock (R&D accumulation)
- `market_shares[i]`: firm i’s market share (sums to 1)
- `effective_demand`: market demand after elasticity and substitutes
- `economic_regime`: `boom` or `recession`
- `supplier_shock`: multiplicative cost shock
- `substitute_pressure`: demand leakage factor in [min, max]

## Constraints
- **Price ceiling**: `P_max`
- **Minimum margin**: `price >= marginal_cost + P_min_margin`
- R&D is clipped to be non-negative.

## Cost shocks and the recent consistency fix

A critical economic consistency bug was fixed in `step()`:

Correct ordering (now enforced):
1. Apply supplier shock → update `marginal_costs`
2. Clip/validate prices using the **updated** `marginal_costs`
3. Compute demand → shares → quantities
4. Compute profit using the **same** `marginal_costs`

This guarantees that **price feasibility** and **profit calculation** are based on the same cost realization.

## Validation

Environment correctness and robustness are covered by:
- `version1/tests/test_market_env_multi_v1.py`
- `tests/test_env_sanity.py` (mechanism tests + extreme edge cases)
