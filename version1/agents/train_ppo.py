import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
import os
from stable_baselines3 import PPO
from stable_baselines3.common.logger import configure

from version1.env.v1_wrappers import make_v1_env


def train():
    # Create environment
    env = make_v1_env(
        n_firms=3,
        max_steps=200,
        num_envs=4,
        normalize_reward=True
    )

    # Logging directory
    log_dir = "version1/experiments/logs"
    os.makedirs(log_dir, exist_ok=True)

    logger = configure(log_dir, ["stdout", "csv"])

    # PPO model
    model = PPO(
        policy="MlpPolicy",
        env=env,
        learning_rate=3e-4,
        n_steps=1024,
        batch_size=256,
        gamma=0.99,
        gae_lambda=0.95,
        ent_coef=0.01,
        clip_range=0.2,
        verbose=1,
    )

    model.set_logger(logger)

    # Train
    model.learn(total_timesteps=300_000)

    # Save model
    model.save("version1/experiments/ppo_market_v1")

    env.close()
    print("✅ Training complete and model saved.")


if __name__ == "__main__":
    train()
