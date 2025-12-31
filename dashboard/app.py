import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import streamlit as st
import pandas as pd
from version1.env.market_env import MarketEnv

st.set_page_config(page_title="AI Strategy Simulator", layout="wide")

# =========================================================
# PREMIUM UI STYLING
# =========================================================
st.markdown("""
<style>

/* ---- App Background ---- */
.main {
    background-color: #0E1117;
}

/* ---- Headings ---- */
h1, h2, h3 {
    color: #EAEAEA;
    font-weight: 700;
}

/* ---- Section Headers ---- */
.section-header {
    padding: 14px 0 8px 0;
    font-size: 22px;
    font-weight: 600;
    color: #EAEAEA;
}

/* ---- KPI Cards ---- */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #161B22, #0E1117);
    border-radius: 14px;
    padding: 18px;
    border: 1px solid #2A2E35;
    box-shadow: 0 8px 24px rgba(0,0,0,0.35);
}

/* ---- Charts ---- */
[data-testid="stLineChart"] {
    background-color: #161B22;
    padding: 14px;
    border-radius: 14px;
    border: 1px solid #2A2E35;
}

/* ---- Thicker chart lines ---- */
.vega-embed svg path {
    stroke-width: 2.2px !important;
}

/* ---- Tables ---- */
[data-testid="stDataFrame"] {
    background-color: #161B22;
    border-radius: 14px;
    border: 1px solid #2A2E35;
}

/* ---- Primary Button ---- */
button[kind="primary"] {
    background-color: #4DA3FF;
    color: black;
    border-radius: 10px;
}

/* ---- Divider ---- */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(to right, transparent, #2A2E35, transparent);
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

    st.markdown(
        '<div class="section-header">🏆 Market Leader</div>',
        unsafe_allow_html=True
    )

    st.metric(
        label="Best Performing Firm",
        value=best_firm,
        delta=f"Total Profit: {best_profit:,.0f}"
    )

    # --------- STRATEGIC INSIGHTS ---------
    st.markdown(
        '<div class="section-header">🧠 Strategic Insights</div>',
        unsafe_allow_html=True
    )


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
    st.markdown(
        '<div class="section-header">🆚 Competitive Comparison</div>',
        unsafe_allow_html=True
    )


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

    # ---- Competitive Insight ----
    best_profit_firm = comparison_df.loc[
        comparison_df["Total Profit"].idxmax(), "Firm"
    ]

    best_share_firm = comparison_df.loc[
        comparison_df["Average Market Share"].idxmax(), "Firm"
    ]    

    st.markdown(f"""
    📌 **Competitive Insight**

    - **{best_profit_firm}** leads in overall profitability, indicating superior strategic execution.
    - **{best_share_firm}** commands the highest average market share, suggesting stronger customer preference or pricing power.

    This highlights that **profit leadership and market dominance do not always coincide**, reinforcing the role of strategic positioning.
    """)



    # ================= PORTER'S FIVE FORCES =================
    st.divider()
    st.markdown(
        '<div class="section-header">🧠 Porter’s Five Forces</div>',
        unsafe_allow_html=True
    )


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

    # ================= MARKET STABILITY SIGNAL =================
    st.markdown(
        '<div class="section-header">🎯 Market Stability Signal</div>',
        unsafe_allow_html=True
    )


    avg_price_volatility = price_df.std().mean()
    avg_profit_volatility = profit_df.std().mean()

    if avg_price_volatility < price_df.mean().mean() * 0.2:
        market_state = "🟢 Stable Market"
        state_msg = "Prices and profits remain relatively predictable. Firms compete on efficiency."
    elif avg_price_volatility < price_df.mean().mean() * 0.5:
        market_state = "🟡 Competitive Market"
        state_msg = "Moderate volatility indicates active but controlled competition."
    else:
        market_state = "🔴 Highly Aggressive Market"
        state_msg = "High volatility reflects intense price wars and unstable profit outcomes."

    st.success(market_state)
    st.write(state_msg)

    # ================= KEY TAKEAWAYS =================
    st.divider()
    st.markdown(
        '<div class="section-header">📌 Key Takeaways</div>',
        unsafe_allow_html=True
    )

    st.markdown(f"""
    <div style="
    border-left: 4px solid #4DA3FF;
    padding: 18px;
    background-color: #0E1117;
    border-radius: 10px;
    line-height: 1.7;
    ">
    <b>Key Takeaways</b><br><br>
    • <b>{best_firm}</b> emerges as the market leader by achieving the highest cumulative profit.<br>
    • The market exhibits a <b>{market_state.split()[1].lower()}</b> competitive structure.<br>
    • Firms maintaining <b>price stability and controlled innovation</b> achieve more sustainable profitability.
    </div>
    """, unsafe_allow_html=True)



    # ================= VISUAL DASHBOARD =================
    st.divider()
    st.markdown("## 📌Market Dynamics Overview ")

    #=================KPI METRICS====================

    col_kpi1, col_kpi2, col_kpi3 = st.columns(3)

    with col_kpi1:
        st.metric("Number of Firms", num_firms)

    with col_kpi2:
        st.metric("Simulation Steps", num_steps)

    with col_kpi3:
        st.metric("Base Demand", base_demand)

    # --------- CHARTS ROW 1 ---------
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prices Over Time**")
        st.line_chart(price_df, height=300,use_container_width=True)

    with col2:
        st.markdown("**Profit Over Time**")
        st.line_chart(profit_df, height=300,use_container_width=True)


    #--------- CHARTS ROW 2 ---------

    st.markdown("**Market Share Over Time**")
    st.line_chart(share_df, height=300,use_container_width=True)

    
    # --------- FINAL SNAPSHOTS---------
    st.markdown(
        '<div class="section-header">📋 Final Snapshot</div>',
        unsafe_allow_html=True
    )


    col_t1, col_t2 = st.columns(2)

    with col_t1:
        st.markdown("### Latest Prices")
        st.dataframe(price_df.tail(1), use_container_width=True)

    with col_t2:
        st.markdown("### Latest Profits")
        st.dataframe(profit_df.tail(1), use_container_width=True)












