import streamlit as st
import pandas as pd
from version1.env.market_env import MarketEnv

st.set_page_config(page_title="AI Strategy Simulator", layout="wide")

st.title("AI-Powered Strategy Simulator")
st.subheader("Version 1 – Virtual Market Dashboard")

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

    # --------- CHARTS ---------
    st.subheader("📈 Market Dynamics")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Prices Over Time**")
        st.line_chart(price_df)

    with col2:
        st.markdown("**Profit Over Time**")
        st.line_chart(profit_df)

    st.markdown("**Market Share Over Time**")
    st.line_chart(share_df)

    
    # --------- TABLES ---------
    st.subheader("📊 Final Values (Last Step)")

    final_prices = price_df.iloc[-1]
    final_profits = profit_df.iloc[-1]
    final_shares = share_df.iloc[-1]

    summary_df = pd.DataFrame({
        "Final Price": final_prices,
        "Final Profit": final_profits,
        "Final Market Share": final_shares
    })

    st.dataframe(summary_df)



