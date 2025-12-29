import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from version1.env.market_env import MarketEnv

st.set_page_config(page_title="AI Strategy Simulator", layout="wide")

# ---------------- PREMIUM UI STYLING ----------------
st.markdown("""
<style>
.main {
    background-color: #0E1117;
}
h1, h2, h3 {
    color: #EAEAEA;
    font-weight: 700;
}

.section-header {
    padding: 12px 0;
    font-size: 22px;
    font-weight: 600;
}
[data-testid="metric-container"] {
    background-color: #161B22;
    border-radius: 12px;
    padding: 16px;
    border: 1px solid #2A2E35;
}
[data-testid="stLineChart"] {
    background-color: #161B22;
    padding: 10px;
    border-radius: 12px;
}
[data-testid="stDataFrame"] {
    background-color: #161B22;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# ---------------- TITLE ----------------
st.title("AI-Powered Strategy Simulator")
st.subheader("Version 1 – Virtual Market Dashboard")

# ---------------- EXECUTIVE SUMMARY ----------------
st.markdown("""
### 📘 Executive Summary
This dashboard simulates competitive market behavior using **AI-driven firms**.
It analyzes **pricing strategy**, **profitability**, and **market dominance** over time,
supporting strategic decision-making and competitive foresight.
""")

st.divider()


# ---------------- SIDEBAR ----------------
st.sidebar.header("Controls")

num_firms = st.sidebar.slider("Number of Firms", 2, 6, 3)
num_steps = st.sidebar.slider("Simulation Steps", 50, 300, 100)
base_demand = st.sidebar.number_input("Base Market Demand", 500, 5000, 1000)

run_simulation = st.sidebar.button("Run Simulation")

# ---------------- MAIN PAGE ----------------
st.write("Adjust the controls from the sidebar and click **Run Simulation**.")

if run_simulation:
    env = MarketEnv(
        n_firms=num_firms,
        max_steps=num_steps,
        base_demand=base_demand
    )

    obs, _ = env.reset()

    # --------- STORAGE ---------
    price_history = []
    profit_history = []
    share_history = []

    st.info("Simulation running...")

    for step in range(num_steps):
        actions = {
            agent: env.action_spaces[agent].sample()
            for agent in env.possible_agents
        }

        obs, rewards, term, trunc, info = env.step(actions)

        price_history.append(env.prices.copy())
        profit_history.append([rewards[a] for a in env.possible_agents])
        share_history.append(env.market_share.copy())

    # --------- CONVERT TO DATAFRAMES ---------
    price_df = pd.DataFrame(price_history, columns=env.possible_agents)
    profit_df = pd.DataFrame(profit_history, columns=env.possible_agents)
    share_df = pd.DataFrame(share_history, columns=env.possible_agents)

    st.success("Simulation completed successfully!")

    # --------- MARKET LEADER INSIGHT ---------
    total_profit = profit_df.sum()
    best_firm = total_profit.idxmax()
    best_profit = total_profit.max()

    st.markdown("## 🏆 Market Leader")
    st.metric(
        label="Best Performing Firm",
        value=best_firm,
        delta=f"Total Profit: {best_profit:,.0f}"
    )

    st.divider()

    # --------- STRATEGIC INSIGHTS ---------
    st.markdown("## 🧠 Strategic Insights")

    avg_price = price_df.mean().mean()
    price_volatility = price_df.std().mean()
    avg_profit = profit_df.mean().mean()

    st.markdown(f"""
    - **Average Market Price:** {avg_price:.2f}  
    - **Price Volatility:** {price_volatility:.2f}  
    - **Average Firm Profit:** {avg_profit:.2f}  

    📌 **Insight:**  
    Higher volatility indicates aggressive competition.  
    Market leader likely benefits from pricing efficiency rather than demand dominance.
    """)

    st.divider()

    # ================= COMPETITIVE COMPARISON =================
    st.divider()
    st.markdown("## 🆚 Competitive Comparison Across Firms")

    comparison_data = []

    for firm in price_df.columns:
        comparison_data.append({
            "Firm": firm,
            "Total Profit": profit_df[firm].sum(),
            "Average Price": price_df[firm].mean(),
            "Price Volatility": price_df[firm].std(),
            "Average Market Share": share_df[firm].mean()
        })

    comparison_df = pd.DataFrame(comparison_data)

    # Formatting for readability (premium feel)
    comparison_df["Total Profit"] = comparison_df["Total Profit"].round(2)
    comparison_df["Average Price"] = comparison_df["Average Price"].round(2)
    comparison_df["Price Volatility"] = comparison_df["Price Volatility"].round(2)
    comparison_df["Average Market Share"] = (comparison_df["Average Market Share"] * 100).round(2)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )


    # ================= PORTER'S FIVE FORCES =================
    st.divider()
    st.markdown("## 🧠 Porter’s Five Forces – Strategic Assessment")

    avg_profit = profit_df.mean().mean()
    profit_dispersion = profit_df.std().mean()
    price_volatility = price_df.std().mean()
    market_concentration = share_df.mean().max()

    # --- Force Calculations ---
    competitive_rivalry = "High" if profit_dispersion > avg_profit * 0.5 else "Moderate"
    threat_of_new_entry = "Low" if market_concentration > 0.5 else "Moderate"
    buyer_power = "High" if price_volatility > price_df.mean().mean() * 0.3 else "Moderate"
    supplier_power = "Low"
    threat_of_substitutes = "Moderate"

    forces_df = pd.DataFrame({
        "Force": [
            "Competitive Rivalry",
            "Threat of New Entrants",
            "Bargaining Power of Buyers",
            "Bargaining Power of Suppliers",
            "Threat of Substitutes"
        ],
        "Assessment": [
            competitive_rivalry,
            threat_of_new_entry,
            buyer_power,
            supplier_power,
            threat_of_substitutes
        ]
    })

    st.dataframe(forces_df, use_container_width=True, hide_index=True)

    # ================= VISUAL DASHBOARD =================
    st.divider()
    st.markdown("## 📌Market dynamic Overview ")

    #=================KPI METRICS====================

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    with col_kpi1:
        st.metric("Number of Firms", num_firms)

    with col_kpi2:
        st.metric("Simulation Steps", num_steps)

    with col_kpi3:
        st.metric("Base Demand", base_demand)
    st.divider()

    # --------- CHARTS ROW 1 ---------
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prices Over Time**")
        st.line_chart(price_df, height=300)

    with col2:
        st.markdown("**Profit Over Time**")
        st.line_chart(profit_df, height=300)

    st.divider()

    #--------- CHARTS ROW 2 ---------

    st.markdown("**Market Share Over Time**")
    st.line_chart(share_df, height=300)

    st.divider()

    
    # --------- TABLES ---------
    st.markdown("## 📋 Final Snapshot")

    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("### Latest Prices")
        st.dataframe(price_df.tail(1), use_container_width=True)

    with col_t2:
        st.markdown("### Latest Profits")
        st.dataframe(profit_df.tail(1), use_container_width=True)









