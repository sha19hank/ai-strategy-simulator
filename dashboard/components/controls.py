"""
Control panel components (sidebar, buttons, selectors)
"""
import streamlit as st
from dashboard.utils.version_config import VERSION_CONFIGS, get_version_config

def render_sidebar():
    """Render left sidebar navigation and controls"""
    
    with st.sidebar:
        st.markdown("# ⚙️ Controls")
        
        st.markdown("---")
        
        # Version selector
        st.markdown("### Version")
        version = st.selectbox(
            "Select Version",
            options=['version1', 'version2'],
            format_func=lambda x: VERSION_CONFIGS[x]['display_name'],
            index=0,
            key='version_selector'
        )
        
        # Experiment selector (placeholder for future)
        st.markdown("### Experiment")
        experiment = st.selectbox(
            "Select Run",
            options=['latest'],
            index=0,
            key='experiment_selector',
            help="Future feature: Select from multiple training runs"
        )
        
        st.markdown("---")
        
        # Info about selected version
        config = get_version_config(version)
        
        with st.expander("ℹ️ Version Info", expanded=False):
            st.markdown(f"**Version:** {config['display_name']}")
            st.markdown(f"**Data Path:** `{config['data_path']}`")
            
            st.markdown("**Features:**")
            for feature, enabled in config['features'].items():
                status = "✅" if enabled else "❌"
                st.markdown(f"- {status} {feature.replace('_', ' ').title()}")
        
        st.markdown("---")
        
        # Show economics toggle
        show_economics = st.checkbox(
            "Show Market Economics",
            value=False,
            key='show_economics',
            help="Display market parameters and economic model details"
        )
        
        st.markdown("---")
        
        # About section
        with st.expander("ℹ️ About", expanded=False):
            st.markdown("""
            **AI Strategy Simulator**
            
            Computational economics platform for studying emergent competitive strategy in oligopolistic markets.
            
            **Version 1:** 3-firm oligopoly with innovation and price competition
            
            **Version 2:** Extended with bankruptcy, market entry, and human-AI play (coming soon)
            
            **Tech Stack:**
            - PettingZoo (multi-agent env)
            - Stable-Baselines3 (PPO)
            - Streamlit (dashboard)
            - Plotly (visualization)
            """)
        
        return {
            'version': version,
            'experiment': experiment,
            'show_economics': show_economics,
            'config': config
        }

def render_run_button():
    """Render the main 'Load Results' button"""
    
    # Check if data already loaded (session state)
    if 'data_loaded' in st.session_state and st.session_state.data_loaded:
        return st.button(
            "🔄 Reload Tournament Data",
            type="primary",
            use_container_width=True,
            help="Reload the tournament CSV (run training first to get new results)"
        )
    else:
        return st.button(
            "📊 Load Tournament Results",
            type="primary",
            use_container_width=True,
            help="Load and visualize tournament data from CSV"
        )

def render_chart_toggles():
    """Render toggles for showing/hiding charts"""
    
    st.markdown("### 📊 Select Charts to Display")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        show_prices = st.checkbox("Prices", value=True, key='show_prices')
        show_profits = st.checkbox("Profits", value=True, key='show_profits')
    
    with col2:
        show_shares = st.checkbox("Market Shares", value=True, key='show_shares')
        show_innovation = st.checkbox("Innovation", value=True, key='show_innovation')
    
    with col3:
        show_hhi = st.checkbox("HHI", value=True, key='show_hhi')
        show_dispersion = st.checkbox("Price Dispersion", value=False, key='show_dispersion')
    
    return {
        'prices': show_prices,
        'profits': show_profits,
        'shares': show_shares,
        'innovation': show_innovation,
        'hhi': show_hhi,
        'dispersion': show_dispersion
    }
