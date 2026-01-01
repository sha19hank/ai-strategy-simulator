from supersuit import pettingzoo_env_to_vec_env_v1, concat_vec_envs_v1
from stable_baselines3.common.vec_env import VecNormalize

from version1.env.market_env import MarketEnv


def make_v1_env(
    n_firms=3,
    max_steps=100,
    num_envs=1,
    normalize_reward=True
):
    # 1. Create ParallelEnv (DO NOT convert to AEC)
    env = MarketEnv(
        n_firms=n_firms,
        max_steps=max_steps
    )

    # 2. Convert ParallelEnv -> VecEnv
    env = pettingzoo_env_to_vec_env_v1(env)

    # 3. Concatenate multiple environments
    env = concat_vec_envs_v1(
        env,
        num_vec_envs=num_envs,
        num_cpus=0,
        base_class="stable_baselines3"
    )

    # 4. Normalize rewards (optional but recommended)
    if normalize_reward:
        env = VecNormalize(env, norm_reward=True, norm_obs=False)

    return env
