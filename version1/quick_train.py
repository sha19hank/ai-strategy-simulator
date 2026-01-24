#!/usr/bin/env python
"""
Quick-start training script for MarketEnvMultiV1.

Trains 3 PPO agents in self-play for 300k timesteps with 4 parallel environments.
Saves models and runs evaluation tournament.

Usage:
    python quick_train.py  # Full training (300k steps, ~30 min)
    python quick_train.py --quick  # Quick demo (10k steps, ~1 min)
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from version1.agents.train_marl import train_self_play, evaluate_agents
from version1.agents.eval_tournament import run_tournament, load_models


def main():
    # Check for quick demo flag
    quick_demo = "--quick" in sys.argv
    
    n_episodes = 50 if quick_demo else 1500
    
    print("\n" + "="*70)
    print(f"MarketEnvMultiV1 SELF-PLAY TRAINING")
    print(f"Mode: {'QUICK DEMO' if quick_demo else 'FULL TRAINING'}")
    print(f"Total episodes: {n_episodes:,}")
    print("="*70)
    
    # Train agents
    print("\n[1/2] Training agents...")
    models, env = train_self_play(
        total_timesteps=1000000,  # UPDATED from 300k to 1M for strategic discovery
        n_episodes=n_episodes,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        log_dir="version1/experiments/logs/training",
        model_save_dir="version1/experiments/models",
    )
    
    print("\n✓ Training complete.")
    print("\n" + "-"*70)
    
    # Run evaluation tournament
    print("\n[2/2] Running evaluation tournament...")
    try:
        # Try to find and load the just-trained models
        model_dir = "version1/experiments/models"
        models = load_models(model_dir)
        
        logs_df = run_tournament(
            models,
            n_episodes=10,
            max_steps=200,
            output_dir="version1/experiments/logs/evaluation",
            render=False,
        )
        
        print("\n✓ Tournament complete.")
        
    except Exception as e:
        print(f"\nNote: Tournament evaluation skipped ({e})")
    
    print("\n" + "="*70)
    print("All done!")
    print("\nResults saved to:")
    print("  - Models: version1/experiments/models/")
    print("  - Logs: version1/experiments/logs/")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
