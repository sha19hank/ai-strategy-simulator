"""
Interactive time-series charts using Plotly
"""
import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from dashboard.utils.styling import COLORS, get_chart_layout
from dashboard.utils.data_loader import calculate_hhi

def render_price_chart(df):
    """Price over time for all firms"""
    fig = go.Figure()
    
    for agent in df['agent'].unique():
        agent_data = df[df['agent'] == agent]
        color = COLORS.get(agent, COLORS['neon_purple'])
        
        # Average price per step across all episodes
        avg_prices = agent_data.groupby('step')['price'].mean()
        
        fig.add_trace(go.Scatter(
            x=avg_prices.index,
            y=avg_prices.values,
            name=agent,
            line=dict(color=color, width=3),
            mode='lines',
            hovertemplate=f'<b>{agent}</b><br>Step: %{{x}}<br>Price: $%{{y:.2f}}<extra></extra>'
        ))
    
    # Add marginal cost reference line
    avg_cost = df.groupby('step')['marginal_cost'].mean()
    fig.add_trace(go.Scatter(
        x=avg_cost.index,
        y=avg_cost.values,
        name='Marginal Cost',
        line=dict(color=COLORS['text_secondary'], width=2, dash='dash'),
        mode='lines',
        hovertemplate='Marginal Cost: $%{y:.2f}<extra></extra>'
    ))
    
    layout = get_chart_layout(title="Prices Over Time", height=400)
    layout['yaxis']['title'] = 'Price ($)'
    layout['xaxis']['title'] = 'Time Step'
    fig.update_layout(**layout)
    
    return fig

def render_profit_chart(df):
    """Cumulative profit over time"""
    fig = go.Figure()
    
    for agent in df['agent'].unique():
        agent_data = df[df['agent'] == agent]
        color = COLORS.get(agent, COLORS['neon_purple'])
        
        # Average cumulative profit per step
        avg_profit = agent_data.groupby('step')['cum_profit'].mean()
        
        fig.add_trace(go.Scatter(
            x=avg_profit.index,
            y=avg_profit.values,
            name=agent,
            line=dict(color=color, width=3),
            mode='lines',
            fill='tonexty' if agent != df['agent'].unique()[0] else None,
            hovertemplate=f'<b>{agent}</b><br>Step: %{{x}}<br>Profit: $%{{y:.0f}}<extra></extra>'
        ))
    
    layout = get_chart_layout(title="Cumulative Profit Over Time", height=400)
    layout['yaxis']['title'] = 'Cumulative Profit ($)'
    layout['xaxis']['title'] = 'Time Step'
    fig.update_layout(**layout)
    
    return fig

def render_market_share_chart(df):
    """Market share evolution (stacked area)"""
    fig = go.Figure()
    
    # Prepare data for stacked area
    agents = sorted(df['agent'].unique())
    
    for agent in agents:
        agent_data = df[df['agent'] == agent]
        color = COLORS.get(agent, COLORS['neon_purple'])
        
        avg_share = agent_data.groupby('step')['market_share'].mean()
        
        fig.add_trace(go.Scatter(
            x=avg_share.index,
            y=avg_share.values * 100,  # Convert to percentage
            name=agent,
            line=dict(color=color, width=2),
            mode='lines',
            stackgroup='one',
            fillcolor=color,
            hovertemplate=f'<b>{agent}</b><br>Step: %{{x}}<br>Share: %{{y:.1f}}%<extra></extra>'
        ))
    
    layout = get_chart_layout(title="Market Share Over Time", height=400)
    layout['yaxis']['title'] = 'Market Share (%)'
    layout['xaxis']['title'] = 'Time Step'
    layout['yaxis']['range'] = [0, 100]
    fig.update_layout(**layout)
    
    return fig

def render_innovation_chart(df):
    """Innovation stock over time"""
    fig = go.Figure()
    
    for agent in df['agent'].unique():
        agent_data = df[df['agent'] == agent]
        color = COLORS.get(agent, COLORS['neon_purple'])
        
        avg_innovation = agent_data.groupby('step')['innovation_stock'].mean()
        
        fig.add_trace(go.Scatter(
            x=avg_innovation.index,
            y=avg_innovation.values,
            name=agent,
            line=dict(color=color, width=3),
            mode='lines',
            hovertemplate=f'<b>{agent}</b><br>Step: %{{x}}<br>Innovation: %{{y:.2f}}<extra></extra>'
        ))
    
    layout = get_chart_layout(title="Innovation Stock Over Time", height=400)
    layout['yaxis']['title'] = 'Innovation Stock'
    layout['xaxis']['title'] = 'Time Step'
    fig.update_layout(**layout)
    
    return fig

def render_hhi_chart(df):
    """HHI (market concentration) over time with regime overlay"""
    hhi_df = calculate_hhi(df)
    
    fig = go.Figure()
    
    # Average HHI across episodes
    avg_hhi = hhi_df.groupby('step')['hhi'].mean()
    
    fig.add_trace(go.Scatter(
        x=avg_hhi.index,
        y=avg_hhi.values,
        name='HHI',
        line=dict(color=COLORS['neon_orange'], width=3),
        mode='lines',
        hovertemplate='HHI: %{y:.3f}<extra></extra>'
    ))
    
    # Add concentration threshold lines
    fig.add_hline(y=0.15, line_dash="dash", line_color=COLORS['text_secondary'],
                  annotation_text="Moderate", annotation_position="right")
    fig.add_hline(y=0.25, line_dash="dash", line_color=COLORS['neon_pink'],
                  annotation_text="High", annotation_position="right")
    fig.add_hline(y=0.50, line_dash="dash", line_color=COLORS['neon_purple'],
                  annotation_text="Monopolistic", annotation_position="right")
    
    # Add economic regime shading
    regime_data = df.groupby('step')['economic_regime'].first()
    
    # Identify boom/recession periods
    for step in regime_data.index:
        regime = regime_data[step]
        if regime == 'boom':
            fig.add_vrect(
                x0=step-0.5, x1=step+0.5,
                fillcolor=COLORS['neon_cyan'], opacity=0.05,
                layer="below", line_width=0,
            )
        elif regime == 'recession':
            fig.add_vrect(
                x0=step-0.5, x1=step+0.5,
                fillcolor=COLORS['neon_pink'], opacity=0.05,
                layer="below", line_width=0,
            )
    
    layout = get_chart_layout(title="Market Concentration (HHI) with Economic Regimes", height=400)
    layout['yaxis']['title'] = 'HHI Index'
    layout['xaxis']['title'] = 'Time Step'
    layout['yaxis']['range'] = [0, 1]
    fig.update_layout(**layout)
    
    return fig

def render_price_dispersion_chart(df):
    """Price dispersion (std dev) over time - indicates price wars"""
    price_std = df.groupby('step')['price'].std()
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=price_std.index,
        y=price_std.values,
        name='Price Dispersion',
        line=dict(color=COLORS['neon_pink'], width=3),
        mode='lines',
        fill='tozeroy',
        fillcolor='rgba(255, 107, 157, 0.2)',
        hovertemplate='Std Dev: $%{y:.2f}<extra></extra>'
    ))
    
    # Add threshold line for price wars
    fig.add_hline(y=5.0, line_dash="dash", line_color=COLORS['neon_orange'],
                  annotation_text="Price War Threshold", annotation_position="right")
    
    layout = get_chart_layout(title="Price Dispersion Over Time", height=400)
    layout['yaxis']['title'] = 'Price Std Dev ($)'
    layout['xaxis']['title'] = 'Time Step'
    fig.update_layout(**layout)
    
    return fig

def render_innovation_vs_share_scatter(df):
    """Scatter plot: Innovation vs Market Share"""
    fig = go.Figure()
    
    # Get final state per firm per episode
    final_step = df['step'].max()
    final_data = df[df['step'] == final_step]
    
    for agent in df['agent'].unique():
        agent_final = final_data[final_data['agent'] == agent]
        color = COLORS.get(agent, COLORS['neon_purple'])
        
        fig.add_trace(go.Scatter(
            x=agent_final['innovation_stock'],
            y=agent_final['market_share'] * 100,
            name=agent,
            mode='markers',
            marker=dict(
                size=12,
                color=color,
                line=dict(color='white', width=1)
            ),
            hovertemplate=f'<b>{agent}</b><br>Innovation: %{{x:.2f}}<br>Share: %{{y:.1f}}%<extra></extra>'
        ))
    
    layout = get_chart_layout(title="Innovation vs Market Share", height=400)
    layout['xaxis']['title'] = 'Innovation Stock'
    layout['yaxis']['title'] = 'Market Share (%)'
    fig.update_layout(**layout)
    
    return fig

def render_final_shares_bar(df):
    """Bar chart of final market shares"""
    final_step = df['step'].max()
    final_data = df[df['step'] == final_step]
    
    avg_shares = final_data.groupby('agent')['market_share'].mean() * 100
    
    fig = go.Figure()
    
    colors = [COLORS.get(agent, COLORS['neon_purple']) for agent in avg_shares.index]
    
    fig.add_trace(go.Bar(
        x=avg_shares.index,
        y=avg_shares.values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=1)
        ),
        text=[f"{v:.1f}%" for v in avg_shares.values],
        textposition='outside',
        hovertemplate='%{x}<br>Market Share: %{y:.1f}%<extra></extra>'
    ))
    
    layout = get_chart_layout(title="Final Market Shares", height=350)
    layout['yaxis']['title'] = 'Market Share (%)'
    layout['xaxis']['title'] = ''
    layout['yaxis']['range'] = [0, 100]
    layout['showlegend'] = False
    fig.update_layout(**layout)
    
    return fig

def render_profit_distribution_bar(df):
    """Bar chart of average episode profits"""
    episode_profits = df.groupby(['episode', 'agent'])['cum_profit'].max()
    avg_profits = episode_profits.groupby('agent').mean()
    
    fig = go.Figure()
    
    colors = [COLORS.get(agent, COLORS['neon_purple']) for agent in avg_profits.index]
    
    fig.add_trace(go.Bar(
        x=avg_profits.index,
        y=avg_profits.values,
        marker=dict(
            color=colors,
            line=dict(color='white', width=1)
        ),
        text=[f"${v:.0f}" for v in avg_profits.values],
        textposition='outside',
        hovertemplate='%{x}<br>Avg Profit: $%{y:.0f}<extra></extra>'
    ))
    
    layout = get_chart_layout(title="Average Episode Profit", height=350)
    layout['yaxis']['title'] = 'Cumulative Profit ($)'
    layout['xaxis']['title'] = ''
    layout['showlegend'] = False
    fig.update_layout(**layout)
    
    return fig
