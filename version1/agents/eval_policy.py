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
    model = PPO.load("version1/experiments/ppo_market_v1")

    obs = env.reset()
    step = 0

    print("\n=== EVALUATING TRAINED STRATEGY ===\n")

    while step < 50:
        action, _ = model.predict(obs, deterministic=True)
        obs, reward, done, info = env.step(action)

        # action shape: (2 * n_firms,)
        n_firms = 3
        prices = action[0::2]
        innovation = action[1::2]

        print(f"Step {step}")
        print(" Prices     :", np.round(prices, 2))
        print(" Innovation :", np.round(innovation, 2))
        print(" Rewards    :", np.round(reward, 2))
        print("-" * 40)

        step += 1

    env.close()


if __name__ == "__main__":
    evaluate()
