#!/usr/bin/env python
"""Quick integrity check for the build."""

import sys

print("\n" + "="*70)
print("BUILD INTEGRITY CHECK")
print("="*70)

# Check imports
try:
    from env.market_env_multi_v1 import MarketEnvMultiV1
    print("[OK] MarketEnvMultiV1 imports successfully")
except Exception as e:
    print(f"[FAIL] MarketEnvMultiV1 import failed: {e}")
    sys.exit(1)

try:
    from agents.train_marl import train_self_play, evaluate_agents
    print("[OK] train_marl imports successfully")
except Exception as e:
    print(f"[FAIL] train_marl import failed: {e}")
    sys.exit(1)

try:
    from agents.eval_tournament import load_models, run_tournament
    print("[OK] eval_tournament imports successfully")
except Exception as e:
    print(f"[FAIL] eval_tournament import failed: {e}")
    sys.exit(1)

# Test basic functionality
try:
    env = MarketEnvMultiV1(n_firms=3, max_steps=200, seed=42)
    obs, info = env.reset()
    actions = {'firm_0': [150, 10], 'firm_1': [150, 10], 'firm_2': [150, 10]}
    obs, rewards, term, trunc, info = env.step(actions)
    reward_vals = [f"{rewards[a]:.0f}" for a in ["firm_0", "firm_1", "firm_2"]]
    print("[OK] Environment runs successfully")
    print(f"   Rewards: {reward_vals}")
except Exception as e:
    print(f"[FAIL] Environment test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("="*70)
print("[PASS] ALL CHECKS PASSED - READY FOR TRAINING")
print("="*70 + "\n")
