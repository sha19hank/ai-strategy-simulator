"""
Data loading utilities for dashboard
"""
import pandas as pd
import os
from pathlib import Path

def load_tournament_data(version='version1', experiment_name=None):
    """
    Load tournament results CSV
    
    Args:
        version: 'version1' or 'version2'
        experiment_name: Optional specific experiment folder (future use)
    
    Returns:
        pd.DataFrame or None if file doesn't exist
    """
    base_path = Path(version) / 'experiments' / 'logs' / 'evaluation'
    csv_path = base_path / 'tournament_results.csv'
    
    if not csv_path.exists():
        return None
    
    try:
        df = pd.read_csv(csv_path)
        return df
    except Exception as e:
        print(f"Error loading data: {e}")
        return None

def get_available_experiments(version='version1'):
    """
    Scan for available experiment runs (future feature)
    
    Returns:
        List of experiment folder names
    """
    experiments_path = Path(version) / 'experiments' / 'logs' / 'evaluation'
    
    if not experiments_path.exists():
        return []
    
    # For now, just return default
    # Future: scan for multiple timestamped runs
    return ['latest']

def calculate_hhi(df):
    """
    Calculate Herfindahl-Hirschman Index per timestep
    
    HHI = Σ(market_share²) for each time step
    
    Args:
        df: Tournament dataframe with market_share column
    
    Returns:
        pd.DataFrame with columns: episode, step, hhi
    """
    hhi_data = df.groupby(['episode', 'step']).apply(
        lambda x: (x['market_share'] ** 2).sum()
    ).reset_index(name='hhi')
    
    return hhi_data

def detect_price_wars(df, threshold=5.0):
    """
    Detect price war episodes
    
    Price war = standard deviation of prices > threshold
    
    Returns:
        List of episode numbers with price wars
    """
    price_dispersion = df.groupby('episode')['price'].std()
    price_war_episodes = price_dispersion[price_dispersion > threshold].index.tolist()
    return price_war_episodes

def classify_firm_strategy(agent_data):
    """
    Classify a firm's strategy based on behavior
    
    Returns:
        String: 'Innovator', 'Price Warrior', 'Follower', 'Generic'
    """
    avg_innovation = agent_data['innovation_stock'].mean()
    avg_price = agent_data['price'].mean()
    avg_cost = agent_data['marginal_cost'].mean()
    markup = ((avg_price - avg_cost) / avg_cost) * 100
    
    # Classification logic
    if avg_innovation > 1.5:
        return 'Innovation Leader'
    elif avg_innovation > 0.5:
        return 'Moderate Innovator'
    elif markup < 5:
        return 'Price Warrior'
    else:
        return 'Generic Follower'

def get_market_summary(df):
    """
    Generate auto-summary of market dynamics
    
    Returns:
        dict with summary statistics and classifications
    """
    # Calculate key metrics
    agents = df['agent'].unique()
    final_step = df['step'].max()
    
    # Final state per firm
    firm_summaries = []
    for agent in agents:
        agent_data = df[df['agent'] == agent]
        final_data = agent_data[agent_data['step'] == final_step]
        
        summary = {
            'agent': agent,
            'final_share': final_data['market_share'].mean(),
            'total_profit': agent_data.groupby('episode')['cum_profit'].max().mean(),
            'avg_price': agent_data['price'].mean(),
            'innovation': agent_data['innovation_stock'].mean(),
            'strategy': classify_firm_strategy(agent_data)
        }
        firm_summaries.append(summary)
    
    # Sort by profit
    firm_summaries = sorted(firm_summaries, key=lambda x: x['total_profit'], reverse=True)
    
    # Market structure
    hhi_df = calculate_hhi(df)
    avg_hhi = hhi_df['hhi'].mean()
    
    if avg_hhi > 0.5:
        market_structure = 'Monopolistic'
    elif avg_hhi > 0.25:
        market_structure = 'Highly Concentrated'
    elif avg_hhi > 0.15:
        market_structure = 'Moderately Concentrated'
    else:
        market_structure = 'Competitive'
    
    # Price wars
    price_wars = detect_price_wars(df)
    
    # Innovation dominance
    innovation_leader = max(firm_summaries, key=lambda x: x['innovation'])
    
    return {
        'firms': firm_summaries,
        'winner': firm_summaries[0],
        'market_structure': market_structure,
        'avg_hhi': avg_hhi,
        'price_wars_detected': len(price_wars) > 0,
        'price_war_episodes': price_wars,
        'innovation_leader': innovation_leader,
        'total_episodes': df['episode'].nunique(),
        'steps_per_episode': df['step'].max() + 1,
    }
