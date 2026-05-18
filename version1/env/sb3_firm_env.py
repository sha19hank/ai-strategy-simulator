"""SB3 (Stable-Baselines3) compatibility wrappers for MarketEnvMultiV1.

Stable-Baselines3 expects a Gymnasium-style single-agent Env.
This wrapper exposes ONE firm as the controllable agent and supplies
actions for the remaining firms via simple opponent policies.

Design goals (Phase 2 / Foundation):
- Minimal, CPU-only, deterministic/reproducible with seeds
- No training logic in the dashboard
- Avoid fragile relative imports
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol

import numpy as np
import gymnasium as gym
from gymnasium import spaces

from version1.env.market_env_multi_v1 import MarketEnvMultiV1


class OpponentPolicy(Protocol):
    def act(self, obs: np.ndarray) -> np.ndarray:  # pragma: no cover
        """Return an action compatible with MarketEnvMultiV1."""


@dataclass
class RandomOpponent:
    """Deterministic (seeded) random opponent for continuous Box actions."""

    action_low: np.ndarray
    action_high: np.ndarray
    rng: np.random.RandomState

    def act(self, obs: np.ndarray) -> np.ndarray:
        del obs
        return self.rng.uniform(self.action_low, self.action_high).astype(np.float32)


@dataclass
class PPOOpponent:
    """Opponent backed by a trained SB3 PPO model."""

    model: object

    def act(self, obs: np.ndarray) -> np.ndarray:
        action, _ = self.model.predict(obs, deterministic=True)
        return np.asarray(action, dtype=np.float32)


class SingleFirmMarketEnv(gym.Env):
    """Gymnasium Env exposing a single firm in the multi-agent market.

    Reward is that firm's per-step profit.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        controlled_agent: str,
        opponents: Optional[Dict[str, OpponentPolicy]] = None,
        *,
        env_kwargs: Optional[dict] = None,
        seed: int = 0,
    ):
        super().__init__()

        self.controlled_agent = controlled_agent
        self._base_seed = int(seed)
        self._episode_idx = 0

        self._env_kwargs = dict(env_kwargs or {})
        self._ma_env = MarketEnvMultiV1(**self._env_kwargs, seed=self._base_seed)

        if controlled_agent not in self._ma_env.agents:
            raise ValueError(
                f"Unknown controlled_agent={controlled_agent}. "
                f"Expected one of {self._ma_env.agents}."
            )

        self.observation_space: spaces.Box = self._ma_env.observation_space(controlled_agent)
        self.action_space: spaces.Box = self._ma_env.action_space(controlled_agent)

        # Build default opponents (random) for any unspecified agents
        self._rng = np.random.RandomState(self._base_seed)
        self._opponents: Dict[str, OpponentPolicy] = dict(opponents or {})

        action_low = np.asarray(self.action_space.low, dtype=np.float32)
        action_high = np.asarray(self.action_space.high, dtype=np.float32)

        for agent in self._ma_env.agents:
            if agent == self.controlled_agent:
                continue
            if agent not in self._opponents:
                self._opponents[agent] = RandomOpponent(
                    action_low=action_low,
                    action_high=action_high,
                    rng=np.random.RandomState(self._base_seed + 10_000 + self._ma_env.agents.index(agent)),
                )

        self._last_obs: Optional[Dict[str, np.ndarray]] = None

    def reset(self, *, seed: Optional[int] = None, options: Optional[dict] = None):
        del options

        # Deterministic but varying episodes: base_seed + episode_idx
        if seed is None:
            seed = self._base_seed + self._episode_idx
        self._episode_idx += 1

        obs, info = self._ma_env.reset(seed=int(seed))
        self._last_obs = obs
        return obs[self.controlled_agent], info.get(self.controlled_agent, {})

    def step(self, action):
        if self._last_obs is None:
            raise RuntimeError("Environment must be reset() before step().")

        # Assemble multi-agent action dict
        actions: Dict[str, np.ndarray] = {self.controlled_agent: np.asarray(action, dtype=np.float32)}
        for agent, policy in self._opponents.items():
            if agent == self.controlled_agent:
                continue
            agent_obs = self._last_obs.get(agent)
            if agent_obs is None:
                # Fallback (env currently uses full observability, so this shouldn't happen)
                agent_obs = self._last_obs[self.controlled_agent]
            actions[agent] = policy.act(agent_obs)

        obs, rewards, terminations, truncations, infos = self._ma_env.step(actions)
        self._last_obs = obs

        controlled_obs = obs[self.controlled_agent]
        reward = float(rewards[self.controlled_agent])
        terminated = bool(terminations[self.controlled_agent])
        truncated = bool(truncations[self.controlled_agent])
        info = infos.get(self.controlled_agent, {})

        return controlled_obs, reward, terminated, truncated, info

    def render(self):  # pragma: no cover
        return self._ma_env.render()

    def close(self):
        self._last_obs = None
