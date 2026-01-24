"""
Market visualization component
Shows baseline market → run simulation → agent representation
"""
import streamlit as st
import plotly.graph_objects as go
from dashboard.utils.styling import COLORS, get_chart_layout

def render_baseline_market():
    """Render empty market state before simulation"""
    st.markdown("### 🏭 Market Canvas")
    
    # Create empty market visualization
    fig = go.Figure()
    
    # Add placeholder circles for 3 firms (empty state)
    fig.add_trace(go.Scatter(
        x=[0.3, 0.5, 0.7],
        y=[0.5, 0.5, 0.5],
        mode='markers+text',
        marker=dict(
            size=[80, 80, 80],
            color=['rgba(255,255,255,0.1)'] * 3,
            line=dict(color=COLORS['border'], width=2)  # Just color and width, no dash
        ),
        text=['—', '—', '—'],
        textfont=dict(size=20, color=COLORS['text_secondary']),
        textposition='middle center',
        hoverinfo='skip',
        showlegend=False
    ))
    
    # Add center "Market" label
    fig.add_annotation(
        x=0.5, y=0.15,
        text="Oligopoly Market (3 Firms)",
        showarrow=False,
        font=dict(size=14, color=COLORS['text_secondary']),
    )
    
    layout = get_chart_layout(title="", height=300)
    layout.update({
        'xaxis': {'visible': False, 'range': [0, 1]},
        'yaxis': {'visible': False, 'range': [0, 1]},
        'margin': {'l': 20, 'r': 20, 't': 20, 'b': 20},
    })
    fig.update_layout(**layout)
    
    st.plotly_chart(fig, use_container_width=True)

def render_market_economics(config):
    """Render collapsible market economics info"""
    with st.expander("📊 Market Economics", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Demand System**")
            st.markdown(f"""
            - Base demand: 1,000 units
            - Price elasticity (ε): 0.015
            - Price sensitivity (α): 0.05
            - Substitute pressure: 5-30%
            """)
            
            st.markdown("**Cost Structure**")
            st.markdown(f"""
            - Marginal cost: $80/unit
            - Capital cost: $30/period
            - Compliance: $10 + variable
            - R&D cost: 0.05·(R&D)²
            """)
        
        with col2:
            st.markdown("**Regulation**")
            st.markdown(f"""
            - Price cap: $250
            - Minimum margin: $1 above cost
            """)
            
            st.markdown("**Market Dynamics**")
            st.markdown(f"""
            - Innovation power (β): 1.5
            - Tech progress: 0.002/year
            - Economic cycles: ±20% demand
            - Supplier shocks: ±5%
            """)

def render_active_market(summary):
    """Render market with active firms after simulation"""
    st.markdown("### 🏭 Market Landscape")
    
    firms = summary['firms']
    
    # Create market visualization with firm nodes
    fig = go.Figure()
    
    # Position firms based on market share (y-axis) and innovation (x-axis)
    for i, firm in enumerate(firms):
        agent_name = firm['agent']
        color = COLORS.get(agent_name, COLORS['neon_purple'])
        
        # Size based on market share
        size = 100 + (firm['final_share'] * 300)
        
        # Position: x = innovation level, y = market share
        x_pos = 0.3 + (i * 0.2)  # Spread horizontally
        y_pos = firm['final_share']  # Vertical position by share
        
        fig.add_trace(go.Scatter(
            x=[x_pos],
            y=[y_pos],
            mode='markers+text',
            marker=dict(
                size=size,
                color=color,
                opacity=0.7,
                line=dict(color=color, width=3)
            ),
            text=f"{agent_name}<br>{firm['final_share']:.1%}",
            textfont=dict(size=12, color='white'),
            textposition='middle center',
            name=agent_name,
            hovertemplate=f"<b>{agent_name}</b><br>" +
                         f"Market Share: {firm['final_share']:.1%}<br>" +
                         f"Profit: ${firm['total_profit']:.0f}<br>" +
                         f"Price: ${firm['avg_price']:.2f}<br>" +
                         f"Innovation: {firm['innovation']:.2f}<br>" +
                         f"Strategy: {firm['strategy']}" +
                         "<extra></extra>"
        ))
    
    layout = get_chart_layout(title="", height=350)
    layout.update({
        'xaxis': {'visible': False, 'range': [0, 1]},
        'yaxis': {
            'title': 'Market Share',
            'range': [0, 1],
            'tickformat': '.0%',
            'gridcolor': COLORS['border'],
        },
        'margin': {'l': 60, 'r': 20, 't': 20, 'b': 20},
        'showlegend': True,
        'legend': dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        )
    })
    fig.update_layout(**layout)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Market structure indicator
    st.markdown(f"**Market Structure:** {summary['market_structure']} (HHI = {summary['avg_hhi']:.3f})")
