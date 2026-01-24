#!/usr/bin/env python
"""Analyze tournament results CSV."""

import pandas as pd
import numpy as np

# Load the tournament results
df = pd.read_csv('version1/experiments/logs/evaluation/tournament_results.csv')

print('=== TOURNAMENT RESULTS ANALYSIS ===\n')
print(f'Total rows: {len(df)}')
print(f'Episodes: {df["episode"].max() + 1}')
print(f'Steps per episode: {df["step"].max() + 1}')
print(f'\nColumns: {list(df.columns)}')

print('\n=== PRICE ANALYSIS ===')
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_data = df[df['agent'] == agent]
    print(f'{agent}:')
    print(f'  Min price: ${agent_data["price"].min():.2f}')
    print(f'  Max price: ${agent_data["price"].max():.2f}')
    print(f'  Avg price: ${agent_data["price"].mean():.2f}')
    print(f'  Std dev: ${agent_data["price"].std():.2f}')

print('\n=== PROFIT ANALYSIS (per episode) ===')
episode_profits = df.groupby(['episode', 'agent'])['cum_profit'].max()
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_profits = episode_profits[episode_profits.index.get_level_values('agent') == agent].values
    print(f'{agent}:')
    print(f'  Min: ${agent_profits.min():.0f}')
    print(f'  Max: ${agent_profits.max():.0f}')
    print(f'  Mean: ${agent_profits.mean():.0f}')
    profitable = (agent_profits > 0).sum() / len(agent_profits) * 100
    print(f'  % Profitable: {profitable:.1f}%')

print('\n=== MARKET SHARES (avg per episode) ===')
episode_shares = df.groupby(['episode', 'agent'])['market_share'].mean()
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_shares = episode_shares[episode_shares.index.get_level_values('agent') == agent].values
    print(f'{agent}: {agent_shares.mean():.1%} (std: {agent_shares.std():.1%})')

print('\n=== INNOVATION (final stock per episode) ===')
episode_innovation = df.groupby(['episode', 'agent'])['innovation_stock'].max()
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_innovation = episode_innovation[episode_innovation.index.get_level_values('agent') == agent].values
    print(f'{agent}: {agent_innovation.mean():.2f} (std: {agent_innovation.std():.2f})')

print('\n=== EFFICIENCY BY REGIME ===')
for regime in df['economic_regime'].unique():
    regime_data = df[df['economic_regime'] == regime]
    print(f'\n{regime.upper()} regime:')
    for agent in ['firm_0', 'firm_1', 'firm_2']:
        agent_data = regime_data[regime_data['agent'] == agent]
        print(f'  {agent}: Price=${agent_data["price"].mean():.2f}, Share={agent_data["market_share"].mean():.1%}')

print('\n=== CORRELATION: PRICE vs PROFIT ===')
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_data = df[df['agent'] == agent]
    corr = agent_data['price'].corr(agent_data['profit_step'])
    print(f'{agent}: {corr:.3f} (higher price -> {"higher" if corr > 0 else "lower"} profit)')

print('\n=== CORRELATION: INNOVATION vs MARKET SHARE ===')
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_data = df[df['agent'] == agent]
    corr = agent_data['innovation_stock'].corr(agent_data['market_share'])
    print(f'{agent}: {corr:.3f} (more innovation -> {"higher" if corr > 0 else "lower"} share)')

print('\n=== PRICE WAR ANALYSIS ===')
price_dispersion = df.groupby('episode')['price'].std()
price_war_threshold = 5.0  # $5+ std dev indicates active competition
price_war_episodes = price_dispersion[price_dispersion > price_war_threshold].index.tolist()
print(f'Price war episodes: {price_war_episodes} ({len(price_war_episodes)}/10)')

if len(price_war_episodes) > 0:
    pw_data = df[df['episode'].isin(price_war_episodes)]
    print(f'\nDuring price wars:')
    print(f'  Avg price range: ${pw_data.groupby("episode")["price"].apply(lambda x: x.max() - x.min()).mean():.2f}')
    print(f'  Avg profit impact: ${pw_data.groupby("episode")["cum_profit"].last().mean():.0f}')
    pw_winners = pw_data.groupby(['episode', 'agent'])['market_share'].mean().groupby('episode').idxmax()
    print(f'  Price war winners: {pw_winners.value_counts().to_dict()}')
else:
    print('No price wars detected (price coordination observed)')

print('\n=== PRICING STRATEGIES ===')
for agent in ['firm_0', 'firm_1', 'firm_2']:
    agent_data = df[df['agent'] == agent]
    avg_price = agent_data['price'].mean()
    avg_cost = agent_data['marginal_cost'].mean()
    markup = ((avg_price - avg_cost) / avg_cost) * 100
    print(f'{agent}:')
    print(f'  Avg markup: {markup:.1f}% above cost')
    print(f'  Price volatility: ${agent_data["price"].std():.2f}')
    print(f'  Min price: ${agent_data["price"].min():.2f}')
    print(f'  Max price: ${agent_data["price"].max():.2f}')
