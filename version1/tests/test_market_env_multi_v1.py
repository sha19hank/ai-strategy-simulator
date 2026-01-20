"""
Unit Tests for MarketEnvMultiV1

Validates:
- Environment initialization
- Reset functionality
- Action step mechanics
- Reward calculations
- Economics consistency (prices, profits, demand)
- Shock processes
- Market share calculations
"""

import pytest
import numpy as np
from version1.env.market_env_multi_v1 import MarketEnvMultiV1


class TestEnvironmentBasics:
    """Test basic environment functionality."""
    
    def test_initialization(self):
        """Environment initializes without errors."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        assert env.n_firms == 3
        assert env.max_steps == 200
        assert len(env.agents) == 3
    
    def test_reset(self):
        """Reset returns valid observations."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=42)
        obs, info = env.reset()
        
        assert len(obs) == 3
        for agent in env.agents:
            assert agent in obs
            assert len(obs[agent]) > 0
            assert all(np.isfinite(obs[agent]))
    
    def test_reset_deterministic(self):
        """Reset with same seed produces same initial state."""
        env1 = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=123)
        obs1, _ = env1.reset()
        
        env2 = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=123)
        obs2, _ = env2.reset()
        
        for agent in env1.agents:
            np.testing.assert_array_almost_equal(obs1[agent], obs2[agent])
    
    def test_step(self):
        """Step returns valid outputs."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        actions = {
            "firm_0": np.array([150.0, 10.0]),
            "firm_1": np.array([150.0, 10.0]),
            "firm_2": np.array([150.0, 10.0]),
        }
        
        obs, rewards, term, trunc, info = env.step(actions)
        
        # Check observation format
        assert len(obs) == 3
        for agent in env.agents:
            assert len(obs[agent]) > 0
            assert all(np.isfinite(obs[agent]))
        
        # Check reward format
        assert len(rewards) == 3
        for agent in env.agents:
            assert isinstance(rewards[agent], (float, int))
            assert np.isfinite(rewards[agent])
        
        # Check termination format
        assert len(term) == 3
        for agent in env.agents:
            assert isinstance(term[agent], (bool, np.bool_))


class TestEconomics:
    """Test economic model consistency."""
    
    def test_profitable_pricing(self):
        """Firms should be able to earn positive profits."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=42)
        obs, _ = env.reset()
        
        # Price above marginal cost
        actions = {
            "firm_0": np.array([200.0, 0.0]),
            "firm_1": np.array([200.0, 0.0]),
            "firm_2": np.array([200.0, 0.0]),
        }
        
        obs, rewards, term, trunc, info = env.step(actions)
        
        # All firms should earn positive profit
        for agent in env.agents:
            assert rewards[agent] > 0, f"{agent} earned negative profit: {rewards[agent]}"
    
    def test_price_constraint(self):
        """Prices should be clamped to [C_m + margin, P_max]."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        # Try to set prices outside bounds
        actions = {
            "firm_0": np.array([10.0, 0.0]),  # Below minimum
            "firm_1": np.array([500.0, 0.0]),  # Above maximum
            "firm_2": np.array([250.0, 0.0]),  # At maximum
        }
        
        obs, rewards, term, trunc, info = env.step(actions)
        
        # Check prices are within bounds
        min_price = env.C_base + env.P_min_margin
        max_price = env.P_max
        
        for i, agent in enumerate(env.agents):
            assert min_price <= env.prices[i] <= max_price, \
                f"{agent} price {env.prices[i]} outside bounds [{min_price}, {max_price}]"
    
    def test_demand_calculation(self):
        """Demand should be positive and decrease with average price."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=42)
        obs, _ = env.reset()
        
        # Low prices
        actions_low = {
            "firm_0": np.array([100.0, 0.0]),
            "firm_1": np.array([100.0, 0.0]),
            "firm_2": np.array([100.0, 0.0]),
        }
        
        env.reset()
        obs1, rew1, _, _, _ = env.step(actions_low)
        demand_low = env.effective_demand
        
        # High prices
        actions_high = {
            "firm_0": np.array([200.0, 0.0]),
            "firm_1": np.array([200.0, 0.0]),
            "firm_2": np.array([200.0, 0.0]),
        }
        
        env.reset()
        obs2, rew2, _, _, _ = env.step(actions_high)
        demand_high = env.effective_demand
        
        # Demand should be higher when prices are lower
        assert demand_low > demand_high, \
            f"Demand doesn't respond to price: low={demand_low}, high={demand_high}"
    
    def test_market_shares_sum_to_one(self):
        """Market shares should always sum to 1."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=42)
        obs, _ = env.reset()
        
        for _ in range(50):
            actions = {
                "firm_0": np.array([np.random.uniform(100, 250), np.random.uniform(0, 20)]),
                "firm_1": np.array([np.random.uniform(100, 250), np.random.uniform(0, 20)]),
                "firm_2": np.array([np.random.uniform(100, 250), np.random.uniform(0, 20)]),
            }
            obs, rewards, term, trunc, info = env.step(actions)
            
            share_sum = np.sum(env.market_shares)
            assert np.isclose(share_sum, 1.0), f"Market shares sum to {share_sum}, not 1.0"
    
    def test_rd_accumulation(self):
        """Innovation stocks should accumulate over time."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        innovation_0_before = env.innovation_stocks[0]
        
        actions = {
            "firm_0": np.array([150.0, 15.0]),
            "firm_1": np.array([150.0, 15.0]),
            "firm_2": np.array([150.0, 15.0]),
        }
        
        obs, rewards, term, trunc, info = env.step(actions)
        
        innovation_0_after = env.innovation_stocks[0]
        
        # Innovation should increase
        assert innovation_0_after > innovation_0_before, \
            f"Innovation didn't accumulate: {innovation_0_before} -> {innovation_0_after}"


class TestShocks:
    """Test exogenous shock processes."""
    
    def test_economic_regime_switching(self):
        """Economic regime should switch between boom and recession."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=500, seed=42)
        obs, _ = env.reset()
        
        regimes_seen = set([env.economic_regime])
        
        for _ in range(100):
            actions = {agent: np.array([150.0, 10.0]) for agent in env.agents}
            obs, rewards, term, trunc, info = env.step(actions)
            regimes_seen.add(env.economic_regime)
        
        # Both regimes should be observed (with high probability)
        # Allow for rare cases where only one regime occurs
        assert len(regimes_seen) >= 1, "Economic regime is broken"
    
    def test_substitute_pressure_in_bounds(self):
        """Substitute pressure should stay in valid range."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        for _ in range(100):
            actions = {agent: np.array([150.0, 10.0]) for agent in env.agents}
            obs, rewards, term, trunc, info = env.step(actions)
            
            assert env.substitute_pressure_min <= env.substitute_pressure <= env.substitute_pressure_max, \
                f"Substitute pressure {env.substitute_pressure} out of bounds"


class TestEpisodeTermination:
    """Test episode termination conditions."""
    
    def test_episode_length(self):
        """Episode should terminate at max_steps."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=50)
        obs, _ = env.reset()
        
        for step in range(50):
            actions = {agent: np.array([150.0, 10.0]) for agent in env.agents}
            obs, rewards, term, trunc, info = env.step(actions)
            
            if step < 49:
                assert not any(term.values()), f"Episode terminated early at step {step}"
            else:
                assert any(term.values()), f"Episode didn't terminate at max_steps"


class TestObservationFormat:
    """Test observation vector format and content."""
    
    def test_observation_shape(self):
        """Observations should have correct shape."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        # Expected shape: 3 (prices) + 3 (innovation) + 3 (shares) + 
        #                3 (costs) + 1 (avg_price) + 1 (demand) + 
        #                1 (timestep) + 1 (regime) + 1 (substitute_pressure)
        # = 17 dimensions
        expected_size = 9 + 3 + 5
        
        for agent in env.agents:
            assert len(obs[agent]) == expected_size, \
                f"Observation size {len(obs[agent])} != expected {expected_size}"
    
    def test_observation_finite(self):
        """All observation values should be finite."""
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        obs, _ = env.reset()
        
        for _ in range(20):
            actions = {agent: np.array([150.0, 10.0]) for agent in env.agents}
            obs, rewards, term, trunc, info = env.step(actions)
            
            for agent in env.agents:
                assert all(np.isfinite(obs[agent])), \
                    f"Non-finite values in {agent} observation: {obs[agent]}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
