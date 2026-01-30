"""
Auto-generated summary component
"What Happened in This Run?"
"""
import streamlit as st
from dashboard.utils.styling import COLORS

def render_summary(summary):
    """Render auto-generated summary of simulation results"""
    
    with st.expander("📋 What Happened in This Run?", expanded=True):
        
        # Header
        st.markdown(f"## Market Outcome: {summary['market_structure']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("HHI (Concentration)", f"{summary['avg_hhi']:.3f}")
        
        with col2:
            st.metric("Episodes Analyzed", summary['total_episodes'])
        
        with col3:
            st.metric("Steps per Episode", summary['steps_per_episode'])
        
        st.markdown("---")
        
        # Winner analysis
        winner = summary['winner']
        st.markdown(f"### 🏆 Winner: **{winner['agent']}**")
        
        st.markdown(f"""
        **Strategy:** {winner['strategy']}
        
        - **Market Share:** {winner['final_share']:.1%}
        - **Average Profit:** ${winner['total_profit']:.0f} per episode
        - **Average Price:** ${winner['avg_price']:.2f}
        - **Innovation Stock:** {winner['innovation']:.2f}
        
        **Why {winner['agent']} won:**
        """)
        
        # Auto-generate win reason
        if winner['innovation'] > 1.5:
            st.markdown(f"✅ Heavy R&D investment created **product superiority**")
        elif winner['innovation'] > 0.5:
            st.markdown(f"✅ Moderate innovation gave **competitive edge**")
        
        if winner['final_share'] > 0.5:
            st.markdown(f"✅ Achieved **near-monopoly** market position")
        
        if winner['total_profit'] > 5000:
            st.markdown(f"✅ Sustained **high profitability** throughout")
        
        st.markdown("---")
        
        # All firms ranking
        st.markdown("### 📊 Firm Rankings")
        
        for i, firm in enumerate(summary['firms'], 1):
            emoji = "🥇" if i == 1 else "🥈" if i == 2 else "🥉"
            color = COLORS.get(firm['agent'], COLORS['neon_purple'])
            
            with st.container():
                st.markdown(f"""
                <div style="background: {COLORS['background_secondary']}; border-left: 4px solid {color}; padding: 15px; border-radius: 8px; margin-bottom: 10px;">
                    <h4 style="margin: 0; color: {color};">{emoji} {firm['agent']} — {firm['strategy']}</h4>
                    <p style="margin: 5px 0; color: {COLORS['text_secondary']};">
                        Market Share: {firm['final_share']:.1%} | 
                        Profit: ${firm['total_profit']:.0f} | 
                        Innovation: {firm['innovation']:.2f}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Market dynamics
        st.markdown("### 🔍 Market Dynamics")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Price competition
            if summary['price_wars_detected']:
                st.markdown("⚔️ **Price Wars Detected**")
                st.markdown(f"Episodes with intense price competition: {summary['price_war_episodes']}")
            else:
                st.markdown("🤝 **Price Coordination Observed**")
                st.markdown("Firms maintained similar pricing throughout")
        
        with col2:
            # Innovation competition
            innov_leader = summary['innovation_leader']
            st.markdown(f"🔬 **Innovation Leader:** {innov_leader['agent']}")
            st.markdown(f"Innovation stock: {innov_leader['innovation']:.2f}")
            
            if innov_leader['innovation'] > 2.0:
                st.markdown("Dominated through heavy R&D investment")
            elif innov_leader['innovation'] > 0.5:
                st.markdown("Moderate innovation strategy")
            else:
                st.markdown("Low/no innovation focus")
        
        # Market structure interpretation
        st.markdown("### 📈 Economic Interpretation")
        
        if summary['avg_hhi'] > 0.5:
            st.markdown("""
            **Monopolistic Market** (HHI > 0.5)
            - One firm dominates with >70% market share
            - Similar to: Google Search, iPhone in premium segment
            - Regulatory concern: High concentration
            """)
        elif summary['avg_hhi'] > 0.25:
            st.markdown("""
            **Highly Concentrated Market** (HHI > 0.25)
            - Clear market leader with 40-70% share
            - Similar to: Pharmaceutical blockbusters, cloud computing
            - Typical oligopoly outcome
            """)
        elif summary['avg_hhi'] > 0.15:
            st.markdown("""
            **Moderately Concentrated** (HHI > 0.15)
            - Multiple strong competitors
            - Similar to: Automotive, consumer electronics
            - Healthy competition observed
            """)
        else:
            st.markdown("""
            **Competitive Market** (HHI < 0.15)
            - No clear dominant firm
            - Similar to: Generic pharmaceuticals, retail
            - Intense competition
            """)
        
        # Real-world analogies
        st.markdown("### 🌍 Real-World Parallels")
        
        winner_strategy = winner['strategy']
        
        if "Innovation Leader" in winner_strategy:
            st.markdown("""
            This outcome mirrors real innovation-driven monopolies:
            - **Pharmaceutical:** Pfizer's Lipitor (60-70% cholesterol drug market)
            - **Tech:** Apple's iPhone (57% US smartphone market)
            - **Search:** Google (92% global search market)
            
            Innovation created a **superior product** that customers preferred despite similar pricing.
            """)
        elif "Price Warrior" in winner_strategy:
            st.markdown("""
            This outcome mirrors price-based competition:
            - **Retail:** Walmart's low-price dominance
            - **Generic drugs:** Teva's market share gains
            - **Airlines:** Southwest's cost leadership
            
            Aggressive pricing captured market share despite lower margins.
            """)
        else:
            st.markdown("""
            Balanced competition with no clear dominant strategy.
            Market shares distributed more evenly across firms.
            """)

def render_compact_summary_cards(summary):
    """Render summary as compact metric cards (alternative layout)"""
    
    col1, col2, col3, col4 = st.columns(4)
    
    winner = summary['winner']
    
    with col1:
        st.metric(
            "Market Leader",
            winner['agent'],
            f"{winner['final_share']:.1%} share"
        )
    
    with col2:
        st.metric(
            "Market Structure",
            summary['market_structure'],
            f"HHI: {summary['avg_hhi']:.3f}"
        )
    
    with col3:
        price_war_status = "Yes" if summary['price_wars_detected'] else "No"
        st.metric(
            "Price Wars",
            price_war_status,
            f"{len(summary['price_war_episodes'])} episodes"
        )
    
    with col4:
        innov_leader = summary['innovation_leader']
        st.metric(
            "Innovation Leader",
            innov_leader['agent'],
            f"{innov_leader['innovation']:.2f} stock"
        )
