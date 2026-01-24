"""
AI Strategy Simulator Dashboard
Dark Neon Analytics Theme
Multi-Agent Oligopoly Market Visualization
"""

# =========================================================
# PATH FIX (required for Streamlit)
# =========================================================
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# =========================================================
# IMPORTS
# =========================================================
import streamlit as st
import pandas as pd

# Dashboard components
from dashboard.components import market_view, charts, summary, controls
from dashboard.utils import data_loader, styling, version_config

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Strategy Simulator",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# APPLY CUSTOM STYLING
# =========================================================
st.markdown(styling.CUSTOM_CSS, unsafe_allow_html=True)

# =========================================================
# INITIALIZE SESSION STATE
# =========================================================
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'df' not in st.session_state:
    st.session_state.df = None
if 'summary' not in st.session_state:
    st.session_state.summary = None

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
sidebar_state = controls.render_sidebar()

# =========================================================
# HEADER SECTION
# =========================================================
col1, col2 = st.columns([3, 1])

with col1:
    st.markdown("""
    <h1 style='background: linear-gradient(135deg, #B794F6, #FF6B9D); 
               -webkit-background-clip: text; 
               -webkit-text-fill-color: transparent;
               font-size: 3em; margin: 0;'>
        AI Strategy Simulator
    </h1>
    <p style='color: #8B949E; font-size: 1.2em; margin: 0;'>
        Multi-Agent Oligopoly Market Visualization
    </p>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div style='text-align: right; padding-top: 10px;'>
        <p style='color: #B794F6; margin: 0; font-size: 0.9em;'>
            {sidebar_state['config']['display_name']}
        </p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# =========================================================
# MARKET VISUALIZATION PANEL
# =========================================================

if not st.session_state.data_loaded:
    # Baseline market (before simulation)
    market_view.render_baseline_market()
    
    # Show economics if toggled
    if sidebar_state['show_economics']:
        market_view.render_market_economics(sidebar_state['config'])
    
    # Load Tournament Results button
    st.markdown("### 📊 Ready to Analyze Tournament Results")
    st.info("""
    **Note:** This dashboard visualizes pre-computed tournament data.
    
    To generate new results, run training first:
    ```bash
    python version1/quick_train.py
    python version1/agents/eval_tournament.py
    ```
    """)
    run_clicked = controls.render_run_button()
    
    if run_clicked:
        # Load data
        with st.spinner(f"Loading tournament data from {sidebar_state['version']}..."):
            df = data_loader.load_tournament_data(sidebar_state['version'])
            
            if df is None:
                st.error(f"""
                ❌ **No tournament data found!**
                
                Expected path: `{sidebar_state['config']['data_path']}/tournament_results.csv`
                
                Please run training and evaluation first:
                ```bash
                python version1/quick_train.py
                python version1/agents/eval_tournament.py
                ```
                """)
            else:
                # Calculate summary
                market_summary = data_loader.get_market_summary(df)
                
                # Store in session state
                st.session_state.df = df
                st.session_state.summary = market_summary
                st.session_state.data_loaded = True
                st.rerun()

else:
    # Data is loaded - show active market
    df = st.session_state.df
    market_summary = st.session_state.summary
    
    # Active market visualization
    market_view.render_active_market(market_summary)
    
    # Show economics if toggled
    if sidebar_state['show_economics']:
        market_view.render_market_economics(sidebar_state['config'])
    
    # Reload button
    if controls.render_run_button():
        st.session_state.data_loaded = False
        st.rerun()
    
    st.markdown("---")
    
    # =========================================================
    # SUMMARY SECTION
    # =========================================================
    summary.render_compact_summary_cards(market_summary)
    
    st.markdown("---")
    
    # =========================================================
    # CHART TOGGLES
    # =========================================================
    chart_toggles = controls.render_chart_toggles()
    
    st.markdown("---")
    
    # =========================================================
    # TIME-SERIES CHARTS
    # =========================================================
    st.markdown("## 📈 Market Dynamics Over Time")
    
    # Row 1: Prices and Profits
    if chart_toggles['prices'] or chart_toggles['profits']:
        col1, col2 = st.columns(2)
        
        with col1:
            if chart_toggles['prices']:
                st.plotly_chart(charts.render_price_chart(df), use_container_width=True)
        
        with col2:
            if chart_toggles['profits']:
                st.plotly_chart(charts.render_profit_chart(df), use_container_width=True)
    
    # Row 2: Market Share and Innovation
    if chart_toggles['shares'] or chart_toggles['innovation']:
        col1, col2 = st.columns(2)
        
        with col1:
            if chart_toggles['shares']:
                st.plotly_chart(charts.render_market_share_chart(df), use_container_width=True)
        
        with col2:
            if chart_toggles['innovation']:
                st.plotly_chart(charts.render_innovation_chart(df), use_container_width=True)
    
    # Row 3: HHI and Price Dispersion
    if chart_toggles['hhi'] or chart_toggles['dispersion']:
        col1, col2 = st.columns(2)
        
        with col1:
            if chart_toggles['hhi']:
                st.plotly_chart(charts.render_hhi_chart(df), use_container_width=True)
        
        with col2:
            if chart_toggles['dispersion']:
                st.plotly_chart(charts.render_price_dispersion_chart(df), use_container_width=True)
    
    st.markdown("---")
    
    # =========================================================
    # DISTRIBUTION & ANALYSIS CHARTS
    # =========================================================
    st.markdown("## 📊 Strategic Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.plotly_chart(charts.render_final_shares_bar(df), use_container_width=True)
    
    with col2:
        st.plotly_chart(charts.render_profit_distribution_bar(df), use_container_width=True)
    
    with col3:
        st.plotly_chart(charts.render_innovation_vs_share_scatter(df), use_container_width=True)
    
    st.markdown("---")
    
    # =========================================================
    # DETAILED SUMMARY
    # =========================================================
    summary.render_summary(market_summary)
    
    st.markdown("---")
    
    # =========================================================
    # DATA EXPORT
    # =========================================================
    with st.expander("💾 Export Data", expanded=False):
        st.markdown("Download the complete tournament dataset:")
        
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name=f"tournament_results_{sidebar_state['version']}.csv",
            mime="text/csv"
        )
        
        st.markdown(f"**Total rows:** {len(df):,}")
        st.markdown(f"**Columns:** {', '.join(df.columns)}")

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #8B949E; padding: 20px;'>
    <p>AI Strategy Simulator | Computational Economics Research Platform</p>
    <p style='font-size: 0.9em;'>Built with Streamlit + Plotly | Dark Neon Analytics Theme</p>
</div>
""", unsafe_allow_html=True)
