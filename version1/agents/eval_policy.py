import sys
import os
import numpy as np
from stable_baselines3 import PPO

# Ensure project root is on path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from version1.env.v1_wrappers import make_v1_env


def evaluate():
    # Create environment
    env = make_v1_env(
        n_firms=3,
        max_steps=50,
        num_envs=1,
        normalize_reward=False
    )

    # Load trained model
    try:
        model = PPO.load("version1/experiments/ppo_market_v1")
    except FileNotFoundError:
        print("❌ Model not found. Please train the model first using train_ppo.py")
        env.close()
        return

    # VecNormalize.reset() returns only obs, not (obs, info)
    obs = env.reset()
    step = 0

    print("\n=== EVALUATING TRAINED STRATEGY ===\n")
    
    n_firms = 3
    all_prices = []
    all_innovation = []
    all_rewards = []

    while step < 50:
        action, _ = model.predict(obs, deterministic=True)
        # VecNormalize wraps step and returns only 4 values: obs, rewards, dones, infos
        result = env.step(action)
        if len(result) == 5:
            obs, rewards, dones, infos, truncs = result
        else:
            obs, rewards, dones, infos = result
            truncs = None

        # action shape: (num_envs * 2 * n_firms,) -> reshape to (num_envs, 2, n_firms)
        # Since num_envs=1, we get (1, 2, 3) -> extract [0] to get (2, 3)
        # Then split into prices and innovation
        num_envs = 1
        action_reshaped = action.reshape(num_envs, -1)  # (1, 6)
        
        # Extract prices and innovation for each firm
        prices = action_reshaped[0, 0::2]  # indices 0, 2, 4
        innovation = action_reshaped[0, 1::2]  # indices 1, 3, 5

        # Rewards is a (num_envs,) array
        episode_reward = rewards[0] if isinstance(rewards, np.ndarray) else rewards

        print(f"Step {step}")
        print(" Prices     :", np.round(prices, 2))
        print(" Innovation :", np.round(innovation, 2))
        print(" Episode Reward    :", np.round(episode_reward, 2))
        print("-" * 40)

        all_prices.append(prices.copy())
        all_innovation.append(innovation.copy())
        all_rewards.append(episode_reward)

        if dones[0]:
            break

        step += 1

    print("\n=== EVALUATION SUMMARY ===")
    print(f"Average Price: {np.mean(all_prices):.2f}")
    print(f"Average Innovation Spend: {np.mean(all_innovation):.2f}")
    print(f"Total Cumulative Reward: {np.sum(all_rewards):.2f}")
    
    env.close()


if __name__ == "__main__":
    evaluate()
