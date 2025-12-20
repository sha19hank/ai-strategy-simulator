from pettingzoo.utils.conversions import parallel_to_aec
from supersuit import (
    pettingzoo_env_to_vec_env_v1,
    concat_vec_envs_v1,
    normalize_reward_v0
)

from version1.env.market_env import MarketEnv


def make_v1_env(
    n_firms=3,
    max_steps=100,
    num_envs=1,
    normalize_reward=True
):
    """
    Creates a vectorized Gym-compatible environment for Version 1
    suitable for Stable-Baselines3 PPO.
    """

    # 1. Create PettingZoo Parallel Environment
    env = MarketEnv(
        n_firms=n_firms,
        max_steps=max_steps
    )

    # 2. Convert ParallelEnv → AEC (required by SuperSuit)
    env = parallel_to_aec(env)

    # 3. Convert PettingZoo → Vectorized Gym Env
    env = pettingzoo_env_to_vec_env_v1(env)

    # 4. Optional: normalize rewards (recommended for PPO stability)
    if normalize_reward:
        env = normalize_reward_v0(env)

    # 5. Concatenate multiple envs (for parallel training)
    env = concat_vec_envs_v1(
        env,
        num_vec_envs=num_envs,
        num_cpus=0,
        base_class="stable_baselines3"
    )

    return env
