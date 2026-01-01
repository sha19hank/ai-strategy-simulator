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
import numpy as np
from stable_baselines3 import PPO

from version1.env.market_env import MarketEnv

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(page_title="AI Strategy Simulator", layout="wide")

# =========================================================
# PREMIUM UI STYLING
# =========================================================
st.markdown("""
<style>
.main { background-color: #0E1117; }
h1, h2, h3 { color: #EAEAEA; font-weight: 700; }
.section-header {
    padding: 14px 0 8px 0;
    font-size: 22px;
    font-weight: 600;
    color: #EAEAEA;
}
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #161B22, #0E1117);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid #2A2E35;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}
[data-testid="stLineChart"] {
    background-color: #161B22;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid #2A2E35;
}
.vega-embed svg path { stroke-width: 2.2px !important; }
[data-testid="stDataFrame"] {
    background-color: #161B22;
    border-radius: 14px;
    border: 1px solid #2A2E35;
}
button[kind="primary"] {
    background-color: #4DA3FF;
    color: black;
    border-radius: 10px;
}
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #2A2E35, transparent);
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# TITLE
# =========================================================
st.title("AI‑Powered Strategy Simulator")
st.subheader("Version 1 – AI‑Trained Virtual Market")

st.markdown("""
### 📘 Executive Summary
This dashboard visualizes **AI‑trained firms** competing in a simulated market.
Firm strategies are learned using **reinforcement learning (PPO)** and reflect
adaptive pricing, innovation investment, and competitive positioning.
""")

st.divider()

# =========================================================
# SIDEBAR CONTROLS
# =========================================================
st.sidebar.header("Controls")
num_firms = st.sidebar.slider("Number of Firms", 2, 6, 3)
num_steps = st.sidebar.slider("Simulation Steps", 50, 300, 100)
base_demand = st.sidebar.number_input("Base Market Demand", 500, 5000, 1000)
run_simulation = st.sidebar.button("Run AI Simulation")

# =========================================================
# MAIN SIMULATION (FIXED)
# =========================================================
if run_simulation:
    st.info("Running AI‑driven market simulation...")

    # -------- ENVIRONMENT --------
    env = MarketEnv(
        n_firms=num_firms,
        max_steps=num_steps,
        base_demand=base_demand
    )

    obs, _ = env.reset()
    obs_dict = obs

    # -------- LOAD TRAINED MODEL --------
    MODEL_PATH = "version1/experiments/ppo_market_v1.zip"
    model = PPO.load(MODEL_PATH)

    # -------- STORAGE --------
    price_history = []
    profit_history = []
    share_history = []

    # -------- ROLLOUT LOOP --------
    for step in range(num_steps):
        flat_obs = next(iter(obs_dict.values()))

        action_vector, _ = model.predict(flat_obs, deterministic=True)

        actions = {
            agent: action_vector[2 * i : 2 * i + 2]
            for i, agent in enumerate(env.possible_agents)
        }

        obs_dict, rewards, terminations, truncations, infos = env.step(actions)

        price_history.append(env.prices.copy())
        profit_history.append([rewards[a] for a in env.possible_agents])
        share_history.append(env.market_share.copy())

        if all(terminations.values()):
            break

    st.success("AI simulation completed successfully!")

    # =========================================================
    # DATAFRAMES
    # =========================================================
    price_df = pd.DataFrame(price_history, columns=env.possible_agents)
    profit_df = pd.DataFrame(profit_history, columns=env.possible_agents)
    share_df = pd.DataFrame(share_history, columns=env.possible_agents)

    # =========================================================
    # MARKET LEADER
    # =========================================================
    total_profit = profit_df.sum()
    best_firm = total_profit.idxmax()

    st.markdown('<div class="section-header">🏆 Market Leader</div>', unsafe_allow_html=True)
    st.metric(
        label="Best Performing Firm",
        value=best_firm,
        delta=f"Total Profit: {total_profit.max():,.0f}"
    )

    # =========================================================
    # STRATEGIC INSIGHTS
    # =========================================================
    st.markdown('<div class="section-header">🧠 Strategic Insights</div>', unsafe_allow_html=True)

    avg_price = price_df.mean().mean()
    price_volatility = price_df.std().mean()
    avg_profit = profit_df.mean().mean()

    st.markdown(f"""
    - **Average Market Price:** {avg_price:.2f}  
    - **Price Volatility:** {price_volatility:.2f}  
    - **Average Firm Profit:** {avg_profit:.2f}  

    📌 **Insight:**  
    Learned strategies favor **price stability and controlled innovation**, leading
    to more sustainable profitability.
    """)

    st.divider()

    # =========================================================
    # COMPETITIVE COMPARISON
    # =========================================================
    st.markdown('<div class="section-header">🆚 Competitive Comparison</div>', unsafe_allow_html=True)

    comparison_df = pd.DataFrame({
        "Firm": env.possible_agents,
        "Total Profit": profit_df.sum().values,
        "Average Price": price_df.mean().values,
        "Price Volatility": price_df.std().values,
        "Average Market Share (%)": share_df.mean().values * 100,
    }).round(2)

    st.dataframe(comparison_df, use_container_width=True, hide_index=True)

    st.divider()

    # =========================================================
    # VISUAL DASHBOARD
    # =========================================================
    st.markdown("## 📊 Market Dynamics Overview")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prices Over Time**")
        st.line_chart(price_df, height=300, use_container_width=True)

    with col2:
        st.markdown("**Profits Over Time**")
        st.line_chart(profit_df, height=300, use_container_width=True)

    st.markdown("**Market Share Over Time**")
    st.line_chart(share_df, height=300, use_container_width=True)

    st.divider()

    # =========================================================
    # FINAL SNAPSHOT
    # =========================================================
    st.markdown('<div class="section-header">📋 Final Snapshot</div>', unsafe_allow_html=True)

    col_f1, col_f2 = st.columns(2)
    with col_f1:
        st.markdown("### Final Prices")
        st.dataframe(price_df.tail(1), use_container_width=True)

    with col_f2:
        st.markdown("### Final Profits")
        st.dataframe(profit_df.tail(1), use_container_width=True)
