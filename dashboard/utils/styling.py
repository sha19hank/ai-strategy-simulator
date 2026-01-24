"""
Dark Neon Analytics Theme Configuration
"""

# Theme Colors
COLORS = {
    'background': '#0e1117',
    'background_secondary': '#161B22',
    'border': '#2A2E35',
    'text_primary': '#EAEAEA',
    'text_secondary': '#8B949E',
    
    # Neon accents
    'neon_purple': '#B794F6',
    'neon_pink': '#FF6B9D',
    'neon_orange': '#FF9E64',
    'neon_cyan': '#7DCFFF',
    
    # Agent colors (consistent across all charts)
    'firm_0': '#FF6B9D',  # Neon pink
    'firm_1': '#B794F6',  # Neon purple
    'firm_2': '#7DCFFF',  # Neon cyan
}

# Chart layout template for Plotly
def get_chart_layout(title="", height=400):
    """Standard layout for all Plotly charts"""
    return {
        'template': 'plotly_dark',
        'height': height,
        'plot_bgcolor': COLORS['background_secondary'],
        'paper_bgcolor': COLORS['background'],
        'font': {'color': COLORS['text_primary'], 'size': 12},
        'title': {
            'text': title,
            'font': {'size': 16, 'color': COLORS['text_primary']},
            'x': 0.5,
            'xanchor': 'center'
        },
        'xaxis': {
            'gridcolor': COLORS['border'],
            'zerolinecolor': COLORS['border'],
        },
        'yaxis': {
            'gridcolor': COLORS['border'],
            'zerolinecolor': COLORS['border'],
        },
        'hovermode': 'x unified',
        'margin': {'l': 60, 'r': 30, 't': 60, 'b': 60},
    }

# Custom CSS for Streamlit
CUSTOM_CSS = """
<style>
/* Global styles */
.main {
    background-color: #0e1117;
}

/* Headers */
h1, h2, h3 {
    color: #EAEAEA !important;
    font-weight: 700 !important;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: linear-gradient(145deg, #161B22, #0E1117);
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #2A2E35;
    box-shadow: 0 0 20px rgba(183, 148, 246, 0.1);
}

[data-testid="metric-container"]:hover {
    border: 1px solid #B794F6;
    box-shadow: 0 0 30px rgba(183, 148, 246, 0.2);
    transition: all 0.3s ease;
}

/* Cards */
.card {
    background: #161B22;
    border-radius: 12px;
    padding: 20px;
    border: 1px solid #2A2E35;
    margin-bottom: 20px;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #B794F6, #FF6B9D);
    color: white;
    border: none;
    border-radius: 8px;
    padding: 12px 32px;
    font-weight: 600;
    font-size: 16px;
    box-shadow: 0 0 20px rgba(183, 148, 246, 0.3);
    transition: all 0.3s ease;
}

.stButton > button:hover {
    box-shadow: 0 0 30px rgba(183, 148, 246, 0.5);
    transform: translateY(-2px);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #0e1117;
    border-right: 1px solid #2A2E35;
}

/* Selectbox */
.stSelectbox > div > div {
    background-color: #161B22;
    border: 1px solid #2A2E35;
    border-radius: 8px;
}

/* Expander */
.streamlit-expanderHeader {
    background-color: #161B22;
    border: 1px solid #2A2E35;
    border-radius: 8px;
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    background-color: #161B22;
    border: 1px solid #2A2E35;
    border-radius: 8px 8px 0 0;
    color: #8B949E;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, #B794F6, #FF6B9D);
    color: white;
    border: none;
}

/* Success/Info boxes */
.stAlert {
    background-color: #161B22;
    border: 1px solid #2A2E35;
    border-radius: 8px;
}
</style>
"""
