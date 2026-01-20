"""
Tournament Evaluation Pipeline

Runs trained agents in a 200-step tournament and logs:
- Prices, quantities, innovation levels
- Market shares and concentration (HHI)
- Cumulative profits per firm
- Competitive dynamics across time
"""

import os
import numpy as np
import pandas as pd
from pathlib import Path
from stable_baselines3 import PPO

from env.market_env_multi_v1 import MarketEnvMultiV1


def load_models(model_dir: str) -> dict:
    """
    Load trained PPO models from directory.
    
    Expected naming: firm_0_*.zip, firm_1_*.zip, firm_2_*.zip
    
    Args:
        model_dir: Path to directory containing saved models
    
    Returns:
        models: Dict[agent_name -> loaded model]
    """
    
    models = {}
    for agent_name in ["firm_0", "firm_1", "firm_2"]:
        # Find most recent model for this agent
        pattern = f"{agent_name}_*.zip"
        matching_files = list(Path(model_dir).glob(pattern))
        
        if not matching_files:
            raise FileNotFoundError(f"No models found matching {pattern} in {model_dir}")
        
        # Use most recently modified
        latest_model = max(matching_files, key=lambda p: p.stat().st_mtime)
        
        print(f"Loading {agent_name} from {latest_model.name}")
        models[agent_name] = PPO.load(str(latest_model))
    
    return models


def run_tournament(
    models: dict,
    n_episodes: int = 10,
    max_steps: int = 200,
    output_dir: str = "version1/experiments/logs/evaluation",
    render: bool = False,
) -> pd.DataFrame:
    """
    Run tournament and log all market dynamics.
    
    Args:
        models: Dict[agent_name -> PPO model]
        n_episodes: Number of independent episodes
        max_steps: Steps per episode
        output_dir: Directory to save CSV logs
        render: Whether to print market state each step
    
    Returns:
        logs: DataFrame with all recorded variables
    """
    
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*70)
    print("TOURNAMENT EVALUATION")
    print("="*70)
    print(f"Episodes: {n_episodes}")
    print(f"Steps per episode: {max_steps}")
    print(f"Output: {output_dir}")
    print("="*70 + "\n")
    
    logs = []
    
    for episode in range(n_episodes):
        print(f"Episode {episode+1}/{n_episodes}")
        
        env = MarketEnvMultiV1(n_firms=3, max_steps=max_steps)
        observations, _ = env.reset()
        
        cumulative_profits = {"firm_0": 0, "firm_1": 0, "firm_2": 0}
        
        for step in range(max_steps):
            # Get actions from trained models
            actions = {}
            for agent in models.keys():
                obs = observations[agent].reshape(1, -1)
                action, _ = models[agent].predict(obs, deterministic=True)
                actions[agent] = action[0]
            
            # Step environment
            observations, rewards, terminations, truncations, infos = env.step(actions)
            
            # Update cumulative profits
            for agent in models.keys():
                cumulative_profits[agent] += rewards[agent]
            
            # Log state
            for i, agent in enumerate(models.keys()):
                log_entry = {
                    "episode": episode,
                    "step": step,
                    "agent": agent,
                    "price": float(env.prices[i]),
                    "rd_investment": float(actions[agent][1]),
                    "innovation_stock": float(env.innovation_stocks[i]),
                    "market_share": float(env.market_shares[i]),
                    "marginal_cost": float(env.marginal_costs[i]),
                    "quantity": float(env.market_shares[i] * env.effective_demand),
                    "profit_step": float(rewards[agent]),
                    "cum_profit": float(cumulative_profits[agent]),
                    "effective_demand": float(env.effective_demand),
                    "economic_regime": env.economic_regime,
                    "substitute_pressure": float(env.substitute_pressure),
                }
                logs.append(log_entry)
            
            if render and step % 20 == 0:
                env.render()
            
            if any(terminations.values()):
                break
        
        # Print episode summary
        print(f"  Final profits: {[f'{cumulative_profits[a]:.0f}' for a in models.keys()]}")
        print()
    
    # Convert to DataFrame
    logs_df = pd.DataFrame(logs)
    
    # ====================================================================
    # AGGREGATE STATISTICS
    # ====================================================================
    
    # Average prices by agent
    avg_prices = logs_df.groupby("agent")["price"].mean()
    print("\nAverage Prices:")
    for agent, price in avg_prices.items():
        print(f"  {agent}: ${price:.2f}")
    
    # Average market shares
    avg_shares = logs_df.groupby("agent")["market_share"].mean()
    print("\nAverage Market Shares:")
    for agent, share in avg_shares.items():
        print(f"  {agent}: {share:.1%}")
    
    # HHI (Herfindahl-Hirschman Index)
    hhi = (avg_shares ** 2).sum()
    print(f"\nMarket Concentration (HHI): {hhi:.4f}")
    print(f"  (1/3 = perfect competition {1/3:.4f}; 1 = monopoly)")
    
    # Average profits per episode
    avg_profits = logs_df.groupby(["episode", "agent"])["cum_profit"].max().groupby("agent").mean()
    print("\nAverage Cumulative Profit (per episode):")
    for agent, profit in avg_profits.items():
        print(f"  {agent}: ${profit:,.0f}")
    
    # Innovation levels
    avg_innovation = logs_df.groupby("agent")["innovation_stock"].max().groupby("agent").mean()
    print("\nAverage Final Innovation Stock:")
    for agent, inno in avg_innovation.items():
        print(f"  {agent}: {inno:.2f}")
    
    # ====================================================================
    # SAVE LOGS
    # ====================================================================
    
    output_path = os.path.join(output_dir, "tournament_results.csv")
    logs_df.to_csv(output_path, index=False)
    print(f"\n✅ Saved tournament logs to {output_path}")
    
    return logs_df


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m version1.agents.eval_tournament <model_dir>")
        print("Example: python -m version1.agents.eval_tournament version1/experiments/models")
        sys.exit(1)
    
    model_dir = sys.argv[1]
    
    # Load models
    models = load_models(model_dir)
    
    # Run tournament
    logs_df = run_tournament(
        models,
        n_episodes=10,
        max_steps=200,
        render=False,
    )
    
    print("\n✅ Evaluation complete.")
