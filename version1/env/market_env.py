import numpy as np
from pettingzoo import ParallelEnv
from gymnasium import spaces

from core.models.demand import compute_demand
from core.models.cost import compute_cost
from core.models.innovation import innovation_effect


class MarketEnv(ParallelEnv):
    """
    Fully virtual competitive market environment (Version 1)

    Each agent represents a firm competing on price and innovation.
    Reward = economic profit.
    """

    metadata = {"name": "market_env_v1"}

    def __init__(
        self,
        n_firms=3,
        max_steps=100,
        base_demand=1000,
        price_bounds=(1.0, 500.0),
        innovation_bounds=(0.0, 50.0),
        marginal_cost=20.0,
        capital_cost=5.0
    ):
        super().__init__()

        self.n_firms = n_firms
        self.max_steps = max_steps
        self.base_demand = base_demand
        self.price_bounds = price_bounds
        self.innovation_bounds = innovation_bounds
        self.marginal_cost = marginal_cost
        self.capital_cost = capital_cost

        self.agents = [f"firm_{i}" for i in range(n_firms)]
        self.possible_agents = self.agents[:]

        # Action space: [price, innovation investment]
        self.action_spaces = {
            agent: spaces.Box(
                low=np.array([price_bounds[0], innovation_bounds[0]]),
                high=np.array([price_bounds[1], innovation_bounds[1]]),
                dtype=np.float32,
            )
            for agent in self.agents
        }

        # Observation space (shared market view)
        self.observation_spaces = {
            agent: spaces.Box(
                low=0.0,
                high=np.inf,
                shape=(n_firms * 3 + 1,),  # prices, shares, innovation + demand
                dtype=np.float32,
            )
            for agent in self.agents
        }

        self.reset()

    def reset(self, seed=None, options=None):
        self.timestep = 0

        self.prices = np.random.uniform(
            self.price_bounds[0], self.price_bounds[1], self.n_firms
        )
        self.innovation = np.zeros(self.n_firms)
        self.market_share = np.ones(self.n_firms) / self.n_firms
        self.demand = self.base_demand

        observations = self._get_observations()
        infos = {agent: {} for agent in self.agents}
        return observations, infos

    def step(self, actions):
        self.timestep += 1

        # Extract actions
        prices = np.array([actions[a][0] for a in self.agents])
        innovation_spend = np.array([actions[a][1] for a in self.agents])

        self.prices = prices
        self.innovation += innovation_spend

        # Compute demand allocation
        firm_demand, market_share = compute_demand(
            prices=self.prices,
            innovation=self.innovation,
            base_demand=self.base_demand
        )

        self.market_share = market_share

        # Compute profits
        rewards = {}
        for i, agent in enumerate(self.agents):
            revenue = self.prices[i] * firm_demand[i]
            cost = compute_cost(
                quantity=firm_demand[i],
                marginal_cost=self.marginal_cost,
                innovation_spend=innovation_spend[i]
            )
            economic_profit = revenue - cost - self.capital_cost
            rewards[agent] = economic_profit

        # Observations
        observations = self._get_observations()

        # Termination
        terminations = {
            agent: self.timestep >= self.max_steps for agent in self.agents
        }
        truncations = {agent: False for agent in self.agents}
        infos = {agent: {} for agent in self.agents}

        if self.timestep >= self.max_steps:
            self.agents = []

        return observations, rewards, terminations, truncations, infos

    def _get_observations(self):
        obs = np.concatenate([
            self.prices,
            self.market_share,
            self.innovation,
            np.array([self.demand])
        ])

        return {agent: obs.copy() for agent in self.agents}

    def render(self):
        print(f"Step {self.timestep}")
        for i, agent in enumerate(self.agents):
            print(
                f"{agent} | Price: {self.prices[i]:.2f} | "
                f"Share: {self.market_share[i]:.2f} | "
                f"Innovation: {self.innovation[i]:.2f}"
            )
