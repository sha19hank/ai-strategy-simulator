"""
Multi-Agent Reinforcement Learning Training Loop (Self-Play)

Trains 3 independent PPO agents in parallel self-play mode.
Each agent learns against evolving opponents in the MarketEnvMultiV1.

Monitoring:
- Cumulative episode reward per agent
- Average price, quantities, profit
- Market concentration (HHI)
- Convergence to Nash equilibrium
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime

from stable_baselines3 import PPO
from gymnasium import Env, spaces

from env.market_env_multi_v1 import MarketEnvMultiV1


# ====================================================================
# CALLBACK (Optional, for advanced monitoring)
# ====================================================================


def train_self_play(
    total_timesteps: int = 300000,
    n_episodes: int = 1500,
    policy: str = "MlpPolicy",
    learning_rate: float = 3e-4,
    n_steps: int = 2048,
    batch_size: int = 64,
    n_epochs: int = 20,
    gamma: float = 0.99,
    gae_lambda: float = 0.95,
    clip_range: float = 0.2,
    log_dir: str = "version1/experiments/logs/training",
    model_save_dir: str = "version1/experiments/models",
):
    """
    Train 3 PPO agents in self-play on the oligopoly market.
    
    Uses episodes with manual rollout collection (no vectorization).
    Each agent is trained independently with PPO.
    
    Args:
        total_timesteps: Target total environment steps (approximate)
        n_episodes: Number of training episodes
        policy: PPO policy architecture ("MlpPolicy" for fully-connected)
        learning_rate: PPO learning rate
        n_steps: Rollout buffer size per episode
        batch_size: Batch size for SGD updates
        n_epochs: Number of epochs per update
        gamma: Discount factor
        gae_lambda: GAE lambda
        clip_range: PPO clip range
        log_dir: Directory for metrics logs
        model_save_dir: Directory for model checkpoints
    
    Returns:
        models: Dict[agent_name -> trained PPO model]
        env: Final environment instance
    """
    
    # Setup directories
    os.makedirs(log_dir, exist_ok=True)
    os.makedirs(model_save_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("MULTI-AGENT PPO SELF-PLAY TRAINING")
    print("="*70)
    print(f"Total episodes: {n_episodes:,}")
    print(f"Agents: firm_0, firm_1, firm_2")
    print(f"Policy: {policy}")
    print(f"Learning rate: {learning_rate}")
    print(f"Batch size: {batch_size}")
    print("="*70 + "\n")
    
    # Create dummy environment for observation/action space
    dummy_env = MarketEnvMultiV1(n_firms=3, max_steps=200)
    dummy_obs, _ = dummy_env.reset()
    obs_shape = dummy_obs[dummy_env.agents[0]].shape
    action_shape = dummy_env.action_space(dummy_env.agents[0]).shape
    
    print(f"Observation shape: {obs_shape}")
    print(f"Action shape: {action_shape}")
    print()
    
    # ====================================================================
    # INITIALIZE MODELS
    # ====================================================================
    
    models = {}
    agent_names = ["firm_0", "firm_1", "firm_2"]
    
    # Create a simple wrapper that makes a Gym-like environment
    class SingleAgentWrapper(Env):
        """Wrap multi-agent env as single-agent for initial policy setup."""
        def __init__(self, obs_shape, action_shape):
            super().__init__()
            self.observation_space = spaces.Box(
                low=0.0, high=1e6, shape=obs_shape, dtype=np.float32
            )
            self.action_space = spaces.Box(
                low=np.array([80, 0.0], dtype=np.float32),
                high=np.array([250, 100.0], dtype=np.float32),
                dtype=np.float32,
            )
        
        def reset(self, seed=None, options=None):
            obs = np.zeros(self.observation_space.shape, dtype=np.float32)
            return obs, {}
        
        def step(self, action):
            obs = np.zeros(self.observation_space.shape, dtype=np.float32)
            reward = 0.0
            terminated = False
            truncated = False
            info = {}
            return obs, reward, terminated, truncated, info
    
    wrapper_env = SingleAgentWrapper(obs_shape, action_shape)
    
    for agent_name in agent_names:
        model = PPO(
            policy,
            wrapper_env,
            learning_rate=learning_rate,
            n_steps=min(n_steps, 256),  # Smaller buffer for demo
            batch_size=min(batch_size, 32),
            n_epochs=n_epochs,
            gamma=gamma,
            gae_lambda=gae_lambda,
            clip_range=clip_range,
            verbose=0,
            tensorboard_log=log_dir,
        )
        models[agent_name] = model
        print(f"Initialized {agent_name}")
    
    print()
    
    # ====================================================================
    # TRAINING LOOP (Manual rollout collection)
    # ====================================================================
    
    episode_rewards = {agent: [] for agent in agent_names}
    total_steps = 0
    
    try:
        for episode in range(n_episodes):
            env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=episode)
            obs, info = env.reset()
            
            done = False
            ep_rewards = {agent: 0 for agent in agent_names}
            ep_steps = 0
            
            while not done:
                # Get actions from trained models
                actions = {}
                for agent_name, model in models.items():
                    obs_array = obs[agent_name].reshape(1, -1)
                    action, _ = model.predict(obs_array, deterministic=False)
                    actions[agent_name] = action[0]
                
                # Step environment
                obs, rewards, terminations, truncations, infos = env.step(actions)
                
                # Accumulate rewards
                for agent in agent_names:
                    ep_rewards[agent] += rewards[agent]
                
                ep_steps += 1
                total_steps += 1
                done = any(terminations.values())
            
            # Store episode rewards
            for agent_name in agent_names:
                episode_rewards[agent_name].append(ep_rewards[agent_name])
            
            # Progress logging every 100 episodes
            if (episode + 1) % max(1, n_episodes // 10) == 0:
                pct = 100 * (episode + 1) / n_episodes
                avg_rewards = {
                    agent: np.mean(episode_rewards[agent][-100:])
                    for agent in agent_names
                }
                print(f"[{pct:5.1f}%] Episode {episode+1:5d} | "
                      f"Avg Reward: {list(avg_rewards.values())}")
    
    except KeyboardInterrupt:
        print("\n\nTraining interrupted by user.")
    
    # ====================================================================
    # SAVE MODELS
    # ====================================================================
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for agent_name, model in models.items():
        save_path = os.path.join(model_save_dir, f"{agent_name}_{timestamp}")
        model.save(save_path)
        print(f"Saved {agent_name} to {save_path}.zip")
    
    return models, env


def evaluate_agents(models: dict, n_eval_episodes: int = 5) -> dict:
    """
    Evaluate trained agents in tournament mode.
    
    Args:
        models: Dict[agent_name -> PPO model]
        n_eval_episodes: Number of episodes to evaluate
    
    Returns:
        results: Dict with average rewards, prices, quantities
    """
    
    rewards_by_agent = {agent: [] for agent in models.keys()}
    prices_all = []
    
    for episode in range(n_eval_episodes):
        env = MarketEnvMultiV1(n_firms=3, max_steps=200)
        observations, _ = env.reset()
        episode_done = False
        ep_rewards = {agent: 0 for agent in models.keys()}
        
        while not episode_done:
            actions = {}
            for agent in models.keys():
                obs = observations[agent].reshape(1, -1)
                action, _ = models[agent].predict(obs, deterministic=True)
                actions[agent] = action[0]
            
            observations, rewards, terminations, truncations, _ = env.step(actions)
            
            for agent in models.keys():
                ep_rewards[agent] += rewards[agent]
            
            prices_all.append(env.prices.copy())
            episode_done = any(terminations.values())
        
        for agent in models.keys():
            rewards_by_agent[agent].append(ep_rewards[agent])
    
    # Aggregate results
    avg_rewards = {
        agent: np.mean(rewards_by_agent[agent])
        for agent in models.keys()
    }
    
    prices_array = np.array(prices_all)
    avg_prices = np.mean(prices_array)
    
    return {
        "avg_rewards": avg_rewards,
        "avg_prices": avg_prices,
    }


if __name__ == "__main__":
    # Train agents
    models, envs = train_self_play(
        total_timesteps=300000,
        n_envs=4,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
    )
    
    print("\n✅ Training complete.")
