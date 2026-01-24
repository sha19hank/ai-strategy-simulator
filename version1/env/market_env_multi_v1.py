"""
MarketEnvMultiV1: Multi-Agent Oligopoly Market Simulator

A PettingZoo ParallelEnv for studying emergent competitive strategy
in a regulated, innovation-driven, cost-volatile market.

Economics: Manufacturing/Pharmaceutical oligopoly with 3 firms competing
on price and R&D investment under regulatory constraints and market shocks.
"""

import numpy as np
from pettingzoo import ParallelEnv
from gymnasium import spaces
from typing import Dict, Tuple


class MarketEnvMultiV1(ParallelEnv):
    """
    Multi-agent oligopoly market environment.
    
    3 firms compete on price and innovation investment.
    Market share determined by softmax competition.
    Profits driven by demand, costs, and regulatory constraints.
    """
    
    metadata = {"name": "MarketEnvMultiV1", "render_modes": []}
    
    def __init__(
        self,
        n_firms: int = 3,
        max_steps: int = 200,
        seed: int = None,
    ):
        """
        Initialize market environment.
        
        Args:
            n_firms: Number of competing firms (fixed)
            max_steps: Episode length (steps = quarters)
            seed: Random seed
        """
        super().__init__()
        
        self.n_firms = n_firms
        self.max_steps = max_steps
        self._rng = np.random.RandomState(seed)
        
        # ================================================================
        # ECONOMIC PARAMETERS (From docs/ECONOMICS.md)
        # ================================================================
        
        # Demand
        self.D0 = 1000.0  # Base market size (units)
        self.price_elasticity = 0.015  # Buyer power (ε)
        
        # Cost structure
        self.C_base = 80.0  # Base marginal cost ($/unit)
        self.C_capital = 30.0  # Fixed capital cost (reduced - was 150)
        self.C_compliance_fixed = 10.0  # Fixed compliance cost (reduced - was 50)
        self.C_compliance_var = 0.02 * self.C_base  # Variable compliance ($/unit)
        self.k_rd = 0.05  # R&D cost coefficient (quadratic)
        
        # Market competition
        self.alpha = 0.05  # Price sensitivity (softmax) - UPDATED to enable price wars
        self.beta0 = 1.5  # Innovation power (base)
        self.beta_tech_progress = 0.002  # Tech progress rate
        self.beta_diminishing = 0.01  # Diminishing returns on innovation
        
        # Regulation
        self.P_max = 250.0  # Price ceiling
        self.P_min_margin = 1.0  # Minimum profit margin above cost
        
        # Exogenous dynamics
        self.boom_multiplier = 1.2
        self.recession_multiplier = 0.8
        self.regime_noise_std = 0.02
        
        # Supplier shock
        self.supplier_shock_std = 0.05
        
        # Substitute pressure
        self.substitute_pressure_min = 0.05
        self.substitute_pressure_max = 0.3
        self.substitute_pressure_drift = 0.005
        
        # ================================================================
        # AGENT SETUP
        # ================================================================
        
        self.agents = [f"firm_{i}" for i in range(n_firms)]
        self.possible_agents = self.agents[:]
        
        # Action space: [price, R&D_investment]
        # Price: [C_m + margin, P_max]
        # R&D: [0, 100] (continuous, unbounded in theory but capped for stability)
        self._action_spaces = {
            agent: spaces.Box(
                low=np.array([self.C_base + self.P_min_margin, 0.0], dtype=np.float32),
                high=np.array([self.P_max, 100.0], dtype=np.float32),
                dtype=np.float32,
            )
            for agent in self.agents
        }
        
        # Observation space: Full state observability
        # [prices (n), innovation_stocks (n), market_shares (n), 
        #  marginal_costs (n), avg_price, demand, time, regime, substitute_pressure]
        obs_size = 3 * n_firms + 6  # 3n + 6 dimensions
        self._observation_spaces = {
            agent: spaces.Box(
                low=0.0,
                high=1e6,  # Upper bound is loose (infinity)
                shape=(obs_size,),
                dtype=np.float32,
            )
            for agent in self.agents
        }
        
        # ================================================================
        # STATE VARIABLES
        # ================================================================
        
        # Market state
        self.timestep = 0
        self.prices = np.zeros(n_firms, dtype=np.float32)
        self.innovation_stocks = np.zeros(n_firms, dtype=np.float32)
        self.market_shares = np.ones(n_firms, dtype=np.float32) / n_firms
        self.marginal_costs = np.ones(n_firms, dtype=np.float32) * self.C_base
        
        # Demand state
        self.total_demand = self.D0
        self.effective_demand = self.D0
        
        # Exogenous shocks
        self.economic_regime = "boom"  # "boom" or "recession"
        self.supplier_shock = 1.0
        self.substitute_pressure = 0.15
        
        # ================================================================
        # RESET MUST BE CALLED BEFORE FIRST STEP
        # ================================================================
    
    def observation_space(self, agent: str) -> spaces.Box:
        """Return observation space for agent."""
        return self._observation_spaces[agent]
    
    def action_space(self, agent: str) -> spaces.Box:
        """Return action space for agent."""
        return self._action_spaces[agent]
    
    # ====================================================================
    # ENVIRONMENT LIFECYCLE
    # ====================================================================
    
    def reset(self, seed=None, options=None):
        """
        Reset environment to initial state.
        
        Returns:
            observations: Dict[agent -> observation]
            infos: Dict[agent -> {}]
        """
        if seed is not None:
            self._rng = np.random.RandomState(seed)
        
        self.timestep = 0
        
        # Initialize prices uniformly in feasible range
        price_min = self.C_base + self.P_min_margin
        price_max = self.P_max
        self.prices = self._rng.uniform(
            price_min, price_max, self.n_firms
        ).astype(np.float32)
        
        # Initialize innovation at zero
        self.innovation_stocks = np.zeros(self.n_firms, dtype=np.float32)
        
        # Initialize equal market shares
        self.market_shares = np.ones(self.n_firms, dtype=np.float32) / self.n_firms
        
        # Initialize marginal costs
        self.marginal_costs = np.ones(self.n_firms, dtype=np.float32) * self.C_base
        
        # Initialize demand
        self.total_demand = self.D0
        self.effective_demand = self.D0
        
        # Initialize exogenous shocks
        self.economic_regime = self._rng.choice(["boom", "recession"])
        self.supplier_shock = self._rng.lognormal(0, self.supplier_shock_std)
        self.substitute_pressure = 0.15
        
        observations = self._get_observations()
        infos = {agent: {} for agent in self.agents}
        
        return observations, infos
    
    def step(self, actions: Dict[str, np.ndarray]):
        """
        Execute one market period.
        
        Args:
            actions: Dict[agent -> [price, R&D]]
        
        Returns:
            observations: Dict[agent -> observation]
            rewards: Dict[agent -> profit]
            terminations: Dict[agent -> done]
            truncations: Dict[agent -> False]
            infos: Dict[agent -> {}]
        """
        self.timestep += 1
        
        # ================================================================
        # 1. UPDATE STATE FROM ACTIONS
        # ================================================================
        
        # Extract and clip prices and R&D
        prices = np.array(
            [actions[agent][0] for agent in self.agents],
            dtype=np.float32
        )
        rd_investments = np.array(
            [actions[agent][1] for agent in self.agents],
            dtype=np.float32
        )
        
        # Hard constraint: enforce price bounds
        prices = np.clip(
            prices,
            self.marginal_costs + self.P_min_margin,
            self.P_max
        )
        
        # Clip R&D to non-negative
        rd_investments = np.maximum(rd_investments, 0.0)
        
        self.prices = prices
        
        # Update innovation stocks (accumulate R&D)
        self.innovation_stocks += rd_investments
        
        # ================================================================
        # 2. EXOGENOUS SHOCKS (Markov regime + stochastic)
        # ================================================================
        
        # Economic cycle (Markov switching + noise)
        if self.economic_regime == "boom":
            # Boom -> Boom with prob 0.95, Boom -> Recession with prob 0.05
            if self._rng.rand() < 0.05:
                self.economic_regime = "recession"
        else:  # recession
            # Recession -> Recession with prob 0.90, Recession -> Boom with prob 0.10
            if self._rng.rand() < 0.10:
                self.economic_regime = "boom"
        
        # Economic cycle multiplier with noise
        cycle_mult = (
            self.boom_multiplier if self.economic_regime == "boom"
            else self.recession_multiplier
        )
        cycle_mult *= self._rng.normal(1.0, self.regime_noise_std)
        
        # Supplier shock (lognormal)
        self.supplier_shock = self._rng.lognormal(0, self.supplier_shock_std)
        
        # Substitute pressure (random walk)
        self.substitute_pressure += self._rng.normal(0, self.substitute_pressure_drift)
        self.substitute_pressure = np.clip(
            self.substitute_pressure,
            self.substitute_pressure_min,
            self.substitute_pressure_max
        )
        
        # ================================================================
        # 3. DEMAND CALCULATION
        # ================================================================
        
        # Base demand with economic cycle
        demand_base = self.D0 * cycle_mult
        
        # Average price (for elasticity calculation)
        avg_price = np.mean(self.prices)
        
        # Price elasticity effect (buyer power)
        elasticity_effect = np.exp(-self.price_elasticity * avg_price)
        
        # Substitute pressure effect
        substitute_effect = 1.0 - self.substitute_pressure
        
        # Effective demand
        self.total_demand = demand_base
        self.effective_demand = demand_base * elasticity_effect * substitute_effect
        
        # ================================================================
        # 4. MARKET SHARE ALLOCATION (Softmax competition)
        # ================================================================
        
        # Innovation effectiveness (time-varying with diminishing returns)
        total_innovation = np.sum(self.innovation_stocks)
        beta = self.beta0 * (1.0 + self.beta_tech_progress * self.timestep)
        if total_innovation > 0:
            beta *= 1.0 / (1.0 + self.beta_diminishing * total_innovation)
        
        # Softmax: S_i = exp(-α·P_i + β·I_i) / Σ exp(...)
        utility = -self.alpha * self.prices + beta * self.innovation_stocks
        utility = utility - np.max(utility)  # Numerical stability
        
        exp_utility = np.exp(utility)
        self.market_shares = exp_utility / np.sum(exp_utility)
        
        # ================================================================
        # 5. QUANTITY & REVENUE
        # ================================================================
        
        quantities = self.market_shares * self.effective_demand
        
        # Update marginal costs (with supplier shock)
        self.marginal_costs = (
            self.C_base * self.supplier_shock * np.ones(self.n_firms)
        ).astype(np.float32)
        
        # ================================================================
        # 6. PROFIT CALCULATION (Reward)
        # ================================================================
        
        rewards = {}
        for i, agent in enumerate(self.agents):
            # Revenue
            revenue = self.prices[i] * quantities[i]
            
            # Costs
            cost_marginal = self.marginal_costs[i] * quantities[i]
            cost_rd = self.k_rd * (rd_investments[i] ** 2)
            cost_capital = self.C_capital
            cost_compliance = self.C_compliance_fixed + self.C_compliance_var * quantities[i]
            
            total_cost = cost_marginal + cost_rd + cost_capital + cost_compliance
            
            # Profit (reward signal)
            profit = revenue - total_cost
            rewards[agent] = float(profit)
        
        # ================================================================
        # 7. TERMINATION & OBSERVATIONS
        # ================================================================
        
        observations = self._get_observations()
        
        # Episode terminates after max_steps
        done = self.timestep >= self.max_steps
        terminations = {agent: done for agent in self.agents}
        truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}
        
        return observations, rewards, terminations, truncations, infos
    
    # ====================================================================
    # HELPERS
    # ====================================================================
    
    def _get_observations(self) -> Dict[str, np.ndarray]:
        """
        Construct full-state observations for all agents.
        
        State = [prices, innovation_stocks, market_shares,
                 marginal_costs, avg_price, effective_demand, timestep, regime_int, substitute_pressure]
        """
        regime_int = 1.0 if self.economic_regime == "boom" else 0.0
        
        obs_vector = np.concatenate([
            self.prices,
            self.innovation_stocks,
            self.market_shares,
            self.marginal_costs,
            [np.mean(self.prices)],  # Average price
            [self.effective_demand],
            [float(self.timestep)],
            [regime_int],
            [self.substitute_pressure],
        ]).astype(np.float32)
        
        # All agents see the same state (full observability)
        return {agent: obs_vector.copy() for agent in self.agents}
    
    def render(self):
        """Print market state."""
        print(f"\n=== Step {self.timestep} ===")
        print(f"Regime: {self.economic_regime.upper()}")
        for i, agent in enumerate(self.agents):
            print(
                f"{agent}: Price=${self.prices[i]:.2f} | "
                f"R&D={self.innovation_stocks[i]:.2f} | "
                f"Share={self.market_shares[i]:.1%} | "
                f"C_m=${self.marginal_costs[i]:.2f}"
            )
        print(f"Demand: {self.total_demand:.0f} | Substitutes: {self.substitute_pressure:.1%}")
