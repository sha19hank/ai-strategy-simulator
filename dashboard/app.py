import streamlit as st
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

    st.success("Simulation started successfully!")

    for step in range(num_steps):
        actions = {
            agent: env.action_spaces[agent].sample()
            for agent in env.possible_agents
        }
        obs, rewards, term, trunc, info = env.step(actions)

    st.write("Simulation finished.")


