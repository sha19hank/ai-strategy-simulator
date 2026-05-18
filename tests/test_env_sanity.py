import inspect
import re
from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pytest

from version1.env.market_env_multi_v1 import MarketEnvMultiV1


@dataclass
class StepSnapshot:
    prices: np.ndarray
    marginal_costs: np.ndarray
    market_shares: np.ndarray
    effective_demand: float
    rewards: Dict[str, float]


def _make_env(*, max_steps: int = 200) -> MarketEnvMultiV1:
    return MarketEnvMultiV1(n_firms=3, max_steps=max_steps)


def _random_actions(env: MarketEnvMultiV1, rng: np.random.RandomState) -> Dict[str, np.ndarray]:
    # Intentionally allow prices below/above bounds and some negative R&D to stress clipping.
    actions: Dict[str, np.ndarray] = {}
    for agent in env.agents:
        price = rng.uniform(0.0, float(env.P_max) * 2.0)
        rd = rng.uniform(-50.0, 150.0)
        actions[agent] = np.array([price, rd], dtype=np.float32)
    return actions


def run_random_episode(env: MarketEnvMultiV1, *, steps: int = 200, rng: np.random.RandomState) -> List[StepSnapshot]:
    snapshots: List[StepSnapshot] = []
    observations, infos = env.reset()
    assert isinstance(observations, dict)
    assert isinstance(infos, dict)

    for _ in range(steps):
        actions = _random_actions(env, rng)
        _, rewards, terminations, truncations, _ = env.step(actions)

        snapshots.append(
            StepSnapshot(
                prices=env.prices.copy(),
                marginal_costs=env.marginal_costs.copy(),
                market_shares=env.market_shares.copy(),
                effective_demand=float(env.effective_demand),
                rewards=dict(rewards),
            )
        )

        if any(terminations.values()) or any(truncations.values()):
            break

    return snapshots


def _expected_profit_for_agent(
    env: MarketEnvMultiV1,
    *,
    agent_index: int,
    price: float,
    quantity: float,
    rd_investment_raw: float,
) -> float:
    # Mirror the environment's dtype/promotion behavior:
    # - revenue and marginal variable cost are computed from float32 state
    # - other components promote to float64 via Python floats
    qty64 = np.float64(quantity)
    price32 = np.float32(price)
    rd32 = np.float32(max(rd_investment_raw, 0.0))

    revenue = price32 * qty64  # float64 (float32 * float64)
    cost_marginal = np.float32(env.marginal_costs[agent_index]) * qty64  # float64

    cost_rd = env.k_rd * (rd32 ** 2)  # float64 (k_rd is Python float)
    cost_capital = env.C_capital  # Python float
    cost_compliance = env.C_compliance_fixed + env.C_compliance_var * qty64  # float64

    total_cost = cost_marginal + cost_rd + cost_capital + cost_compliance  # float64
    profit = revenue - total_cost  # float64
    return float(profit)


def test_price_feasibility():
    """CRITICAL: After every step, price must be feasible under current marginal costs."""
    env = _make_env(max_steps=200)
    rng = np.random.RandomState(123)

    for ep in range(10):
        env.reset(seed=1000 + ep)
        for _ in range(200):
            actions = _random_actions(env, rng)
            env.step(actions)

            assert np.all(
                env.prices >= env.marginal_costs + env.P_min_margin
            ), f"Infeasible price detected. prices={env.prices}, costs={env.marginal_costs}, margin={env.P_min_margin}"


def test_price_bounds_not_inverted():
    """IMPORTANT: lower bound (cost+margin) must never exceed P_max."""
    env = _make_env(max_steps=10)
    rng = np.random.RandomState(456)

    env.reset(seed=999)
    for _ in range(10):
        actions = _random_actions(env, rng)
        env.step(actions)

        lb = env.marginal_costs + env.P_min_margin
        if not np.all(lb <= env.P_max):
            raise AssertionError(
                "Price lower bound exceeds upper bound. "
                f"marginal_costs={env.marginal_costs}, P_min_margin={env.P_min_margin}, P_max={env.P_max}, lb={lb}"
            )


def test_no_double_cost_update_check():
    """Ensure marginal costs are set exactly once inside step() and match supplier_shock."""
    # Static check: step() should contain a single assignment to self.marginal_costs.
    src = inspect.getsource(MarketEnvMultiV1.step)
    assignments = re.findall(r"\bself\.marginal_costs\s*=", src)
    assert len(assignments) == 1, f"Expected exactly 1 marginal_costs assignment in step(), found {len(assignments)}"

    # Runtime check: marginal_costs must match C_base * supplier_shock at end of step.
    env = _make_env(max_steps=5)
    rng = np.random.RandomState(789)

    env.reset(seed=42)
    for _ in range(5):
        actions = _random_actions(env, rng)
        env.step(actions)

        expected = (env.C_base * env.supplier_shock) * np.ones(env.n_firms, dtype=np.float32)
        assert np.allclose(env.marginal_costs, expected, atol=1e-6), (
            f"marginal_costs mismatch. got={env.marginal_costs}, expected={expected}, supplier_shock={env.supplier_shock}"
        )


def test_profit_consistency():
    """Rewards must equal the profit formula using the same marginal_costs used for feasibility."""
    env = _make_env(max_steps=50)
    rng = np.random.RandomState(321)

    env.reset(seed=2024)

    for _ in range(50):
        actions = _random_actions(env, rng)
        _, rewards, _, _, _ = env.step(actions)

        quantities = env.market_shares * env.effective_demand

        for i, agent in enumerate(env.agents):
            expected_profit = _expected_profit_for_agent(
                env,
                agent_index=i,
                price=float(env.prices[i]),
                quantity=float(quantities[i]),
                rd_investment_raw=float(actions[agent][1]),
            )
            assert abs(expected_profit - float(rewards[agent])) < 1e-5, (
                f"Profit mismatch for {agent}. expected={expected_profit}, got={rewards[agent]}"
            )


def test_random_rollout_stability_no_nans():
    """Random rollouts should not produce NaNs in core economic variables."""
    rng = np.random.RandomState(9999)

    for ep in range(5):
        env = _make_env(max_steps=200)
        env.reset(seed=5000 + ep)

        for _ in range(200):
            actions = _random_actions(env, rng)
            _, rewards, terminations, truncations, _ = env.step(actions)

            assert not np.isnan(env.prices).any()
            assert not np.isnan(env.marginal_costs).any()
            assert not np.isnan(env.market_shares).any()
            assert not np.isnan(env.effective_demand)
            assert not np.isnan(list(rewards.values())).any()

            if any(terminations.values()) or any(truncations.values()):
                break


def test_demand_and_shares_sanity():
    """Demand must be non-negative; shares must be a valid probability simplex."""
    env = _make_env(max_steps=200)
    rng = np.random.RandomState(2468)

    env.reset(seed=111)
    for _ in range(200):
        actions = _random_actions(env, rng)
        env.step(actions)

        assert env.effective_demand >= 0.0
        assert np.all(env.market_shares >= 0.0)
        assert abs(float(np.sum(env.market_shares)) - 1.0) < 1e-5


def test_reproducibility_same_seed_same_actions():
    """Two envs with same seed + same actions must produce identical trajectories."""
    steps = 100

    action_rng = np.random.RandomState(1357)
    action_seq: List[Dict[str, np.ndarray]] = []

    env_for_agents = _make_env(max_steps=steps)
    env_for_agents.reset(seed=777)

    for _ in range(steps):
        action_seq.append(_random_actions(env_for_agents, action_rng))

    env1 = _make_env(max_steps=steps)
    env2 = _make_env(max_steps=steps)

    env1.reset(seed=777)
    env2.reset(seed=777)

    for t in range(steps):
        a = action_seq[t]

        _, r1, term1, trunc1, _ = env1.step(a)
        _, r2, term2, trunc2, _ = env2.step(a)

        np.testing.assert_allclose(env1.prices, env2.prices, atol=0.0, rtol=0.0)
        np.testing.assert_allclose(env1.marginal_costs, env2.marginal_costs, atol=0.0, rtol=0.0)
        np.testing.assert_allclose(env1.market_shares, env2.market_shares, atol=0.0, rtol=0.0)
        assert float(env1.effective_demand) == float(env2.effective_demand)

        for agent in env1.agents:
            assert float(r1[agent]) == float(r2[agent])

        assert term1 == term2
        assert trunc1 == trunc2

        if any(term1.values()) or any(trunc1.values()):
            break


def test_price_clipping_behavior():
    """CRITICAL mechanism test: clearly invalid low prices must clip to (cost + margin)."""
    env = _make_env(max_steps=5)

    env.reset(seed=123)
    actions = {agent: np.array([0.0, 0.0], dtype=np.float32) for agent in env.agents}
    env.step(actions)

    expected_lb = env.marginal_costs + env.P_min_margin
    assert np.allclose(env.prices, expected_lb, atol=1e-5), (
        f"Prices not clipped to lower bound. prices={env.prices}, expected_lb={expected_lb}"
    )


def test_price_upper_bound_clipping():
    """Extremely high prices must clip to the price ceiling (P_max)."""
    env = _make_env(max_steps=5)

    env.reset(seed=456)
    actions = {agent: np.array([10.0 * float(env.P_max), 0.0], dtype=np.float32) for agent in env.agents}
    env.step(actions)

    assert np.all(env.prices <= env.P_max + 1e-6), f"Upper bound clipping failed. prices={env.prices}, P_max={env.P_max}"


def test_extreme_supplier_shock_stability():
    """Extreme supplier shock variance should not produce NaNs/inf in core variables."""
    env = _make_env(max_steps=50)
    env.supplier_shock_std = 2.5

    rng = np.random.RandomState(999)
    env.reset(seed=999)

    for _ in range(25):
        actions = _random_actions(env, rng)
        _, rewards, terminations, truncations, _ = env.step(actions)

        assert np.isfinite(env.marginal_costs).all(), f"Non-finite marginal_costs: {env.marginal_costs}"
        assert np.isfinite(env.prices).all(), f"Non-finite prices: {env.prices}"
        assert np.isfinite(env.market_shares).all(), f"Non-finite market_shares: {env.market_shares}"
        assert np.isfinite(env.effective_demand), f"Non-finite effective_demand: {env.effective_demand}"
        assert np.isfinite(list(rewards.values())).all(), f"Non-finite rewards: {rewards}"

        if any(terminations.values()) or any(truncations.values()):
            break


def test_low_demand_stability():
    """Very low demand regimes should remain numerically stable and rewards finite."""
    env = _make_env(max_steps=20)
    env.D0 = 1.0
    env.reset(seed=2025)

    env.substitute_pressure = env.substitute_pressure_max
    env.economic_regime = "recession"

    rng = np.random.RandomState(2025)
    for _ in range(20):
        # Force demand suppression via high prices; clipping will apply.
        actions = {agent: np.array([10.0 * float(env.P_max), 0.0], dtype=np.float32) for agent in env.agents}
        _, rewards, terminations, truncations, _ = env.step(actions)

        assert env.effective_demand >= 0.0
        assert np.isfinite(env.effective_demand)
        assert np.isfinite(env.prices).all()
        assert np.isfinite(env.marginal_costs).all()
        assert np.isfinite(list(rewards.values())).all()

        if any(terminations.values()) or any(truncations.values()):
            break


def test_numerical_stability_extreme_values():
    """Extreme but finite actions should not cause overflow/inf in state or rewards."""
    env = _make_env(max_steps=10)
    env.reset(seed=8080)

    # Large R&D (but below float32 overflow when squared) + very high prices.
    big_rd = 1e9
    actions = {agent: np.array([10.0 * float(env.P_max), big_rd], dtype=np.float32) for agent in env.agents}

    for _ in range(10):
        _, rewards, terminations, truncations, _ = env.step(actions)

        assert not np.isinf(env.prices).any()
        assert not np.isinf(env.marginal_costs).any()
        assert not np.isinf(env.innovation_stocks).any()
        assert not np.isinf(env.market_shares).any()
        assert not np.isinf(env.effective_demand)
        assert not np.isinf(list(rewards.values())).any()

        assert np.isfinite(env.prices).all()
        assert np.isfinite(env.marginal_costs).all()
        assert np.isfinite(env.innovation_stocks).all()
        assert np.isfinite(env.market_shares).all()
        assert np.isfinite(env.effective_demand)
        assert np.isfinite(list(rewards.values())).all()

        if any(terminations.values()) or any(truncations.values()):
            break
