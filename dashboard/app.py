import streamlit as st

st.set_page_config(page_title="AI Strategy Simulator", layout="wide")

st.title("AI-Powered Strategy Simulator")
st.subheader("Version 1 – Dashboard")

st.sidebar.header("Controls")

num_firms = st.sidebar.slider("Number of Firms", 2, 6, 3)
num_steps = st.sidebar.slider("Simulation Steps", 50, 300, 100)
base_demand = st.sidebar.number_input("Base Market Demand", 500, 5000, 1000)


st.write("Dashboard setup complete.")

